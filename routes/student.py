from flask import Blueprint, render_template, request, jsonify, session
from database.connection import query
from utils.auth import login_required, role_required
from datetime import date, timedelta, datetime

student_bp = Blueprint('student', __name__)


def _get_student(user_id):
    """Fetch student record for the logged-in user."""
    return query(
        """SELECT s.*, c.name as class_name, c.grade, c.section
           FROM students s
           JOIN classes c ON s.class_id = c.id
           WHERE s.user_id = %s""",
        (user_id,), fetch_one=True
    )


# ── Dashboard ─────────────────────────────────────────────────
@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    uid = session.get('user_id')
    print(f">>> [DASH] Entering dashboard for user_id={uid}", flush=True)
    
    try:
        student = _get_student(uid)
    except Exception as e:
        print(f">>> [DASH] CRITICAL: _get_student crashed: {e}", flush=True)
        return "Database Error: Could not fetch student profile.", 500

    if not student:
        print(f">>> [DASH] User {uid} has no student record", flush=True)
        return render_template('student/dashboard.html', student=None, error="Profile not found.")

    # DEFENSIVE QUERY WRAPPING
    def safe_query(label, sql, params=()):
        try:
            res = query(sql, params)
            return res or []
        except Exception as e:
            print(f">>> [DASH] WARN: {label} query failed: {e}", flush=True)
            return []

    cid = student.get('class_id')
    sid = student.get('id')

    upcoming_tests = safe_query("tests",
        """SELECT t.id, t.name, t.test_date, t.max_marks, t.portions, t.test_type, s.name as subject_name
           FROM tests t JOIN subjects s ON t.subject_id = s.id
           WHERE t.class_id = %s AND t.test_date >= CURDATE()
           ORDER BY t.test_date ASC LIMIT 6""", (cid,))

    upcoming_homework = safe_query("homework",
        """SELECT h.id, h.title, h.description, h.deadline, h.assigned_date, s.name as subject_name, hs.status as submission_status
           FROM homework h JOIN subjects s ON h.subject_id = s.id
           LEFT JOIN homework_submissions hs ON hs.homework_id = h.id AND hs.student_id = %s
           WHERE h.class_id = %s AND h.deadline >= CURDATE()
           ORDER BY h.deadline ASC LIMIT 6""", (sid, cid))

    try:
        att_stats = query("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present FROM student_attendance WHERE student_id = %s", (sid,), fetch_one=True)
        att_pct = round((att_stats['present'] / att_stats['total']) * 100) if att_stats and att_stats.get('total', 0) > 0 else 0
    except:
        att_pct = 0

    notices = safe_query("notices", "SELECT id, title, posted_at FROM notices WHERE is_active = 1 ORDER BY posted_at DESC LIMIT 5")
    remarks = safe_query("remarks", "SELECT r.remark, r.date, CONCAT(t.first_name, ' ', t.last_name) as teacher_name FROM student_remarks r JOIN teachers t ON r.teacher_id = t.id WHERE r.student_id = %s ORDER BY r.date DESC LIMIT 2", (sid,))
    borrowed_books = safe_query("library", "SELECT b.title, bw.due_date, bw.status FROM borrowings bw JOIN books b ON bw.book_id = b.id JOIN library_members lm ON bw.member_id = lm.id WHERE lm.user_id = %s AND bw.status != 'Returned' LIMIT 3", (uid,))

    hw_pending = sum(1 for hw in upcoming_homework if not hw.get('submission_status') or hw['submission_status'] != 'Submitted')

    print(f">>> [DASH] Dashboard data assembled for {student.get('first_name')}", flush=True)

    return render_template('student/dashboard.html',
        student=student, upcoming_tests=upcoming_tests, upcoming_homework=upcoming_homework,
        notices=notices, remarks=remarks, borrowed_books=borrowed_books,
        attendance_pct=att_pct, test_count=len(upcoming_tests), hw_pending=hw_pending,
        active_page='dashboard', today=date.today()
    )


# ── Assignments ───────────────────────────────────────────────
@student_bp.route('/assignments')
@login_required
@role_required('student')
def assignments():
    student = _get_student(session['user_id'])
    if not student:
        return render_template('student/assignments.html', student=None)

    # All homework for this class
    all_homework = query(
        """SELECT h.id, h.title, h.description, h.deadline, h.assigned_date,
                  s.name as subject_name,
                  hs.status as submission_status, hs.submitted_at, hs.feedback, hs.grade
           FROM homework h
           JOIN subjects s ON h.subject_id = s.id
           LEFT JOIN homework_submissions hs
                ON hs.homework_id = h.id AND hs.student_id = %s
           WHERE h.class_id = %s
           ORDER BY h.deadline DESC""",
        (student['id'], student['class_id'])
    ) or []

    upcoming_tests = query(
        """SELECT t.id, t.name, t.test_date, t.max_marks, t.portions, t.test_type,
                  s.name as subject_name
           FROM tests t
           JOIN subjects s ON t.subject_id = s.id
           WHERE t.class_id = %s AND t.test_date >= CURDATE()
           ORDER BY t.test_date ASC
           LIMIT 6""",
        (student['class_id'],)
    ) or []

    scores = query(
        """SELECT ts.marks_obtained, ts.grade, ts.remarks,
                  t.name as test_name, t.max_marks, t.test_type, t.test_date,
                  s.name as subject_name
           FROM test_scores ts
           JOIN tests t ON ts.test_id = t.id
           JOIN subjects s ON t.subject_id = s.id
           WHERE ts.student_id = %s
           ORDER BY t.test_date DESC""",
        (student['id'],)
    ) or []

    completed = [hw for hw in all_homework if hw.get('submission_status') == 'Submitted']
    pending = [hw for hw in all_homework if not hw.get('submission_status') or hw['submission_status'] != 'Submitted']

    return render_template('student/assignments.html',
        student=student,
        completed=completed,
        pending=pending,
        scores=scores,
        upcoming_tests=upcoming_tests,
        active_page='assignments',
        today=date.today()
    )


# ── Mark Complete (AJAX) ─────────────────────────────────────
@student_bp.route('/mark-complete', methods=['POST'])
@login_required
@role_required('student')
def mark_complete():
    student = _get_student(session['user_id'])
    if not student:
        return jsonify({'success': False, 'error': 'Student not found'}), 404

    data = request.get_json()
    item_id = data.get('item_id')
    item_type = data.get('item_type')

    if not item_id or not item_type:
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    try:
        if item_type == 'homework':
            # Check if already submitted
            existing = query(
                "SELECT id FROM homework_submissions WHERE homework_id = %s AND student_id = %s",
                (item_id, student['id']), fetch_one=True
            )
            if existing:
                return jsonify({'success': True, 'message': 'Already completed'})

            query(
                """INSERT INTO homework_submissions (homework_id, student_id, status)
                   VALUES (%s, %s, 'Submitted')""",
                (item_id, student['id']), commit=True
            )
        elif item_type == 'test':
            # For tests, we just acknowledge — no DB change needed for "studied"
            pass

        return jsonify({'success': True})
    except Exception as e:
        print(f"Error marking complete: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500


# ── Attendance ────────────────────────────────────────────────
@student_bp.route('/attendance')
@login_required
@role_required('student')
def attendance():
    student = _get_student(session['user_id'])
    if not student:
        return render_template('student/attendance.html', student=None)

    records = query(
        """SELECT date, status
           FROM student_attendance
           WHERE student_id = %s
           ORDER BY date DESC
           LIMIT 60""",
        (student['id'],)
    ) or []

    # Stats
    total = len(records)
    present = sum(1 for r in records if r['status'] == 'Present')
    absent = sum(1 for r in records if r['status'] == 'Absent')
    late = sum(1 for r in records if r['status'] == 'Late')
    pct = round((present / total) * 100) if total > 0 else 0

    # Process records for the calendar JS
    att_map = {r['date'].strftime('%Y-%m-%d'): r['status'].lower() for r in records}

    return render_template('student/attendance.html',
        student=student,
        records=records,
        att_map=att_map,
        total=total, present=present, absent=absent, late=late,
        attendance_pct=pct,
        active_page='attendance'
    )


# ── Grades ────────────────────────────────────────────────────
@student_bp.route('/grades')
@login_required
@role_required('student')
def grades():
    student = _get_student(session['user_id'])
    if not student:
        return render_template('student/grades.html', student=None)

    scores = query(
        """SELECT ts.marks_obtained, ts.grade, ts.remarks,
                  t.name as test_name, t.max_marks, t.test_type, t.test_date,
                  s.name as subject_name
           FROM test_scores ts
           JOIN tests t ON ts.test_id = t.id
           JOIN subjects s ON t.subject_id = s.id
           WHERE ts.student_id = %s
           ORDER BY t.test_date DESC""",
        (student['id'],)
    ) or []

    # Group by subject
    by_subject = {}
    for score in scores:
        subj = score['subject_name']
        if subj not in by_subject:
            by_subject[subj] = []
        by_subject[subj].append(score)

    return render_template('student/grades.html',
        student=student,
        scores=scores,
        by_subject=by_subject,
        active_page='grades'
    )


# ── Timetable ────────────────────────────────────────────────
@student_bp.route('/timetable')
@login_required
@role_required('student')
def timetable():
    student = _get_student(session['user_id'])
    if not student:
        return render_template('student/timetable.html', student=None)

    entries = query(
        """SELECT ct.day_of_week, ct.room,
                  p.period_number, p.start_time, p.end_time, p.is_break, p.break_name,
                  s.name as subject_name,
                  CONCAT(t.first_name, ' ', t.last_name) as teacher_name
           FROM class_timetable ct
           JOIN periods p ON ct.period_id = p.id
           LEFT JOIN subjects s ON ct.subject_id = s.id
           LEFT JOIN teachers t ON ct.teacher_id = t.id
           WHERE ct.class_id = %s
           ORDER BY FIELD(ct.day_of_week, 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'),
                    p.period_number""",
        (student['class_id'],)
    ) or []

    # Also get all periods for the grid structure
    periods = query(
        "SELECT * FROM periods ORDER BY start_time",
    ) or []

    # Build grid: {period_number: {day: entry}}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    grid = {}
    for p in periods:
        pn = p['period_number']
        grid[pn] = {
            'period': p,
            'slots': {}
        }

    for entry in entries:
        pn = entry['period_number']
        day = entry['day_of_week']
        if pn in grid:
            grid[pn]['slots'][day] = entry

    today_day = datetime.now().strftime('%A')  # e.g. 'Monday'

    return render_template('student/timetable.html',
        student=student,
        grid=grid,
        periods=periods,
        days=days,
        today_name=today_day,
        today=date.today(),
        active_page='timetable'
    )


# ── Profile ───────────────────────────────────────────────────
@student_bp.route('/profile')
@login_required
@role_required('student')
def profile():
    student = _get_student(session['user_id'])

    # Extra stats for academic overview on profile
    att_pct = 0
    scores_count = 0
    hw_done = 0

    if student:
        att_stats = query(
            """SELECT COUNT(*) as total,
                 SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
               FROM student_attendance WHERE student_id = %s""",
            (student['id'],), fetch_one=True
        )
        if att_stats and att_stats['total'] and att_stats['total'] > 0:
            att_pct = round((att_stats['present'] / att_stats['total']) * 100)

        scores_count_row = query(
            "SELECT COUNT(*) as cnt FROM test_scores WHERE student_id = %s",
            (student['id'],), fetch_one=True
        )
        scores_count = scores_count_row['cnt'] if scores_count_row else 0

        hw_done_row = query(
            "SELECT COUNT(*) as cnt FROM homework_submissions WHERE student_id = %s AND status = 'Submitted'",
            (student['id'],), fetch_one=True
        )
        hw_done = hw_done_row['cnt'] if hw_done_row else 0

    return render_template('student/profile.html',
        student=student,
        attendance_pct=att_pct,
        scores_count=scores_count,
        hw_done=hw_done,
        active_page='profile'
    )


# ── Communication (Samvaad) ──────────────────────────────────
@student_bp.route('/communication')
@login_required
@role_required('student')
def communication():
    student = _get_student(session['user_id'])
    if not student:
        return render_template('student/communication.html', student=None)
    
    sid = student.get('id')
    notices = query("SELECT * FROM notices WHERE is_active = 1 ORDER BY posted_at DESC LIMIT 10") or []
    remarks = query("SELECT r.remark, r.date, CONCAT(t.first_name, ' ', t.last_name) as teacher_name, s.name as subject_name FROM student_remarks r JOIN teachers t ON r.teacher_id = t.id JOIN subjects s ON r.subject_id = s.id WHERE r.student_id = %s ORDER BY r.date DESC LIMIT 10", (sid,)) or []
    
    return render_template('student/communication.html',
        student=student,
        notices=notices,
        remarks=remarks,
        active_page='communication',
        today=date.today()
    )
