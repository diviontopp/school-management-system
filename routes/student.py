from flask import Blueprint, render_template, request, jsonify, session
from database.connection import query
from utils.auth import login_required, role_required
from datetime import date, timedelta

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
    student = _get_student(session['user_id'])
    if not student:
        print(f">>> CRITICAL: Student record missing for user_id={session['user_id']} (username={session.get('username')})", flush=True)
        return render_template('student/dashboard.html', student=None, error="Student record not found.")

    # Upcoming tests (next 30 days)
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

    # Upcoming homework (pending, not submitted by this student)
    upcoming_homework = query(
        """SELECT h.id, h.title, h.description, h.deadline, h.assigned_date,
                  s.name as subject_name,
                  hs.status as submission_status
           FROM homework h
           JOIN subjects s ON h.subject_id = s.id
           LEFT JOIN homework_submissions hs
                ON hs.homework_id = h.id AND hs.student_id = %s
           WHERE h.class_id = %s AND h.deadline >= CURDATE()
           ORDER BY h.deadline ASC
           LIMIT 6""",
        (student['id'], student['class_id'])
    ) or []

    # Quick stats
    # Attendance percentage
    att_stats = query(
        """SELECT
             COUNT(*) as total,
             SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
           FROM student_attendance
           WHERE student_id = %s""",
        (student['id'],), fetch_one=True
    )
    att_pct = 0
    if att_stats and att_stats['total'] and att_stats['total'] > 0:
        att_pct = round((att_stats['present'] / att_stats['total']) * 100)

    test_count = len(upcoming_tests)
    hw_pending = sum(1 for hw in upcoming_homework if not hw.get('submission_status') or hw['submission_status'] != 'Submitted')

    return render_template('student/dashboard.html',
        student=student,
        upcoming_tests=upcoming_tests,
        upcoming_homework=upcoming_homework,
        attendance_pct=att_pct,
        test_count=test_count,
        hw_pending=hw_pending,
        active_page='dashboard',
        today=date.today()
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
                  hs.status as submission_status, hs.submitted_at
           FROM homework h
           JOIN subjects s ON h.subject_id = s.id
           LEFT JOIN homework_submissions hs
                ON hs.homework_id = h.id AND hs.student_id = %s
           WHERE h.class_id = %s
           ORDER BY h.deadline DESC""",
        (student['id'], student['class_id'])
    ) or []

    completed = [hw for hw in all_homework if hw.get('submission_status') == 'Submitted']
    pending = [hw for hw in all_homework if not hw.get('submission_status') or hw['submission_status'] != 'Submitted']

    return render_template('student/assignments.html',
        student=student,
        completed=completed,
        pending=pending,
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

    return render_template('student/attendance.html',
        student=student,
        records=records,
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

    return render_template('student/timetable.html',
        student=student,
        grid=grid,
        periods=periods,
        days=days,
        active_page='timetable'
    )


# ── Profile ───────────────────────────────────────────────────
@student_bp.route('/profile')
@login_required
@role_required('student')
def profile():
    student = _get_student(session['user_id'])
    return render_template('student/profile.html',
        student=student,
        active_page='profile'
    )
