-- ============================================================
-- School Portal — Seed Data for Testing
-- Run AFTER schema.sql
-- ============================================================

USE school_portal;

-- ── Classes ────────────────────────────────────────────────
INSERT IGNORE INTO classes (name, grade, section, academic_year) VALUES
('10-A', 10, 'A', '2025-2026'),
('10-B', 10, 'B', '2025-2026'),
('12-A', 12, 'A', '2025-2026');

-- ── Subjects ───────────────────────────────────────────────
INSERT IGNORE INTO subjects (name, code) VALUES
('Mathematics',      'MATH'),
('English',          'ENG'),
('Science',          'SCI'),
('History',          'HIST'),
('Geography',        'GEO'),
('Computer Science', 'CS'),
('Physical Education','PE'),
('Art',              'ART'),
('Hindi',            'HINDI'),
('Chemistry',        'CHEM');

-- ── Users: Admin ────────────────────────────────────────────
-- password: admin123 (bcrypt — will be re-hashed by Flask on first run)
INSERT INTO users (role, username, password_hash) VALUES
('admin', 'admin', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

-- ── Users: Teachers ────────────────────────────────────────
INSERT INTO users (role, username, password_hash) VALUES
('teacher', 'T001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('teacher', 'T002', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('teacher', 'T003', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

-- ── Teachers ───────────────────────────────────────────────
-- user_id 2 = T001, 3 = T002, 4 = T003
INSERT IGNORE INTO teachers (user_id, employee_id, first_name, last_name, department, email, qualification) VALUES
(2, 'T001', 'Priya',    'Sharma',  'Mathematics', 'priya.sharma@school.edu',  'M.Sc Mathematics'),
(3, 'T002', 'Rohit',    'Verma',   'English',     'rohit.verma@school.edu',   'M.A. English'),
(4, 'T003', 'Ananya',   'Singh',   'Science',     'ananya.singh@school.edu',  'M.Sc Physics');

-- ── Users: Students ────────────────────────────────────────
-- password = birthdate DDMMYYYY (bcrypt of 01012010 etc.)
-- Using same hash for demo — real passwords set when students are created
INSERT INTO users (role, username, password_hash) VALUES
('student', 'DBX001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('student', 'DBX002', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('student', 'DBX003', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

-- ── Students ───────────────────────────────────────────────
-- user_id 5 = DBX001, 6 = DBX002, 7 = DBX003
INSERT IGNORE INTO students (user_id, admission_number, first_name, last_name, date_of_birth, gender, class_id, roll_number, email) VALUES
(5, 'DBX001', 'Meera',   'Patel', '2010-01-15', 'F', 1, 1, 'meera.patel@student.school.edu'),
(6, 'DBX002', 'Arjun',   'Kumar', '2010-03-22', 'M', 1, 2, 'arjun.kumar@student.school.edu'),
(7, 'DBX003', 'Shruti',  'Nair',  '2010-07-08', 'F', 2, 1, 'shruti.nair@student.school.edu');

-- ── Users: Parents ─────────────────────────────────────────
INSERT IGNORE INTO users (role, username, password_hash) VALUES
('parent', 'parent001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe');

INSERT IGNORE INTO parents (user_id, first_name, last_name, phone, email, relationship) VALUES
(8, 'Ramesh', 'Patel', '9876543210', 'ramesh.patel@gmail.com', 'Father');

INSERT IGNORE INTO parent_student (parent_id, student_id) VALUES (1, 1);

-- ── Periods ────────────────────────────────────────────────
INSERT IGNORE INTO periods (period_number, start_time, end_time, is_break, break_name) VALUES
(1,  '08:00:00', '08:45:00', FALSE, NULL),
(2,  '08:45:00', '09:30:00', FALSE, NULL),
(3,  '09:30:00', '10:15:00', FALSE, NULL),
(0,  '10:15:00', '10:30:00', TRUE,  'Short Break'),
(4,  '10:30:00', '11:15:00', FALSE, NULL),
(5,  '11:15:00', '12:00:00', FALSE, NULL),
(0,  '12:00:00', '12:45:00', TRUE,  'Lunch Break'),
(6,  '12:45:00', '13:30:00', FALSE, NULL),
(7,  '13:30:00', '14:15:00', FALSE, NULL),
(8,  '14:15:00', '15:00:00', FALSE, NULL);

-- ── Class ↔ Subjects ─────────────────────────────────────
INSERT IGNORE INTO class_subjects (class_id, subject_id, teacher_id) VALUES
(1, 1, 1),   -- 10-A  Math     Priya
(1, 2, 2),   -- 10-A  English  Rohit
(1, 3, 3),   -- 10-A  Science  Ananya
(2, 1, 1),   -- 10-B  Math     Priya
(2, 2, 2);   -- 10-B  English  Rohit

-- ── Sample Books ───────────────────────────────────────────
INSERT IGNORE INTO books (title, author, isbn, publisher, category, total_copies, available_copies, is_recommended) VALUES
('The Alchemist',              'Paulo Coelho',     '9780062315007', 'HarperOne',         'Fiction',  3, 3, TRUE),
('A Brief History of Time',    'Stephen Hawking',  '9780553380163', 'Bantam Books',      'Science',  2, 2, TRUE),
('To Kill a Mockingbird',      'Harper Lee',       '9780061935466', 'Harper Perennial',  'Fiction',  2, 2, FALSE),
('Wings of Fire',              'A.P.J. Abdul Kalam','9788173711466','Universities Press','Biography',4, 4, TRUE),
('The Diary of a Young Girl',  'Anne Frank',       '9780553296983', 'Bantam Books',      'History',  2, 2, FALSE);

-- ── Sample Clubs ───────────────────────────────────────────
INSERT IGNORE INTO clubs (name, description, category, faculty_advisor_id, max_members, is_active) VALUES
('Science Club',    'Explore the wonders of science through experiments and projects.', 'Academic', 3, 30, TRUE),
('Debate Club',     'Build your public speaking and argumentative skills.',             'Academic', 2, 25, TRUE),
('Art & Craft Club','Express creativity through various art forms.',                   'Cultural',  1, 20, TRUE);

-- ============================================================
-- STUDENT DASHBOARD SEED DATA
-- ============================================================

-- ── Tests (upcoming for class 10-A, class_id=1) ────────────
INSERT IGNORE INTO tests (name, subject_id, class_id, test_date, max_marks, portions, test_type, created_by) VALUES
('Unit Test 3 - Quadratics',     1, 1, DATE_ADD(CURDATE(), INTERVAL 3 DAY),  25, 'Quadratic equations, factoring, discriminant', 'Unit Test', 1),
('Mid-Term Exam',                2, 1, DATE_ADD(CURDATE(), INTERVAL 7 DAY),  50, 'Chapters 5-9: Poetry, Grammar, Comprehension', 'Mid Term',  2),
('Science Quiz - Optics',        3, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY),  20, 'Reflection, Refraction, Lenses',               'Quiz',      3),
('Math Monthly Test',            1, 1, DATE_ADD(CURDATE(), INTERVAL 14 DAY), 50, 'Trigonometry, Coordinate Geometry',             'Unit Test', 1),
('English Grammar Test',         2, 1, DATE_ADD(CURDATE(), INTERVAL 5 DAY),  25, 'Tenses, Active-Passive Voice, Reported Speech', 'Quiz',      2);

-- ── Homework (for class 10-A) ──────────────────────────────
INSERT IGNORE INTO homework (title, description, subject_id, class_id, assigned_by, assigned_date, deadline) VALUES
('Solve Exercise 4.2',          'Complete all questions from exercise 4.2 on quadratic equations.', 1, 1, 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 DAY)),
('Essay: My Favorite Season',   'Write a 500-word essay about your favorite season with literary devices.', 2, 1, 2, DATE_SUB(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 1 DAY)),
('Science Lab Report',          'Write the observation and conclusion for the light refraction experiment.', 3, 1, 3, DATE_SUB(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 4 DAY)),
('Math Practice Set 5',        'Practice problems on trigonometric identities, page 112-115.', 1, 1, 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 7 DAY)),
('Read Chapter 8',              'Read chapter 8 and answer comprehension questions at the end.', 2, 1, 2, DATE_SUB(CURDATE(), INTERVAL 3 DAY), DATE_ADD(CURDATE(), INTERVAL 2 DAY));

-- ── Student Attendance (for student_id=1, Meera Patel) ─────
INSERT IGNORE INTO student_attendance (student_id, date, status, marked_by) VALUES
(1, DATE_SUB(CURDATE(), INTERVAL 1 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 2 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 3 DAY),  'Absent',  1),
(1, DATE_SUB(CURDATE(), INTERVAL 4 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 5 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 6 DAY),  'Late',    1),
(1, DATE_SUB(CURDATE(), INTERVAL 7 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 8 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 9 DAY),  'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 10 DAY), 'Absent',  1),
(1, DATE_SUB(CURDATE(), INTERVAL 11 DAY), 'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 12 DAY), 'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 13 DAY), 'Late',    1),
(1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 'Present', 1),
(1, DATE_SUB(CURDATE(), INTERVAL 15 DAY), 'Present', 1);

-- ── Test Scores (past tests for student_id=1) ──────────────
INSERT IGNORE INTO tests (id, name, subject_id, class_id, test_date, max_marks, portions, test_type, created_by) VALUES
(100, 'Unit Test 1 - Algebra',  1, 1, DATE_SUB(CURDATE(), INTERVAL 30 DAY), 25, 'Linear equations, polynomials', 'Unit Test', 1),
(101, 'English Quiz 1',         2, 1, DATE_SUB(CURDATE(), INTERVAL 25 DAY), 20, 'Grammar and vocabulary',       'Quiz',      2),
(102, 'Science Unit Test',      3, 1, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 25, 'Chemical reactions, acids',     'Unit Test', 3);

INSERT IGNORE INTO test_scores (test_id, student_id, marks_obtained, grade, remarks, updated_by) VALUES
(100, 1, 22, 'A',  'Excellent work!',   1),
(101, 1, 17, 'A',  'Good comprehension', 2),
(102, 1, 19, 'B+', 'Needs more practice on balancing equations', 3);

-- ── Timetable (class 10-A, Mon-Fri) ────────────────────────
-- Period 1-3, then break (period_id for break ~ id=4), period 4-5, lunch (id=7), period 6-8
-- Assuming period IDs: 1=P1, 2=P2, 3=P3, 4=ShortBreak, 5=P4, 6=P5, 7=Lunch, 8=P6, 9=P7, 10=P8

INSERT IGNORE INTO class_timetable (class_id, day_of_week, period_id, subject_id, teacher_id, room) VALUES
-- Monday
(1, 'Monday',    1, 1, 1, 'R101'), -- Math
(1, 'Monday',    2, 2, 2, 'R101'), -- English
(1, 'Monday',    3, 3, 3, 'Lab1'), -- Science
(1, 'Monday',    5, 1, 1, 'R101'), -- Math
(1, 'Monday',    6, 2, 2, 'R101'), -- English
(1, 'Monday',    8, 3, 3, 'Lab1'), -- Science
(1, 'Monday',    9, 1, 1, 'R101'), -- Math
-- Tuesday
(1, 'Tuesday',   1, 2, 2, 'R101'),
(1, 'Tuesday',   2, 3, 3, 'Lab1'),
(1, 'Tuesday',   3, 1, 1, 'R101'),
(1, 'Tuesday',   5, 2, 2, 'R101'),
(1, 'Tuesday',   6, 3, 3, 'Lab1'),
(1, 'Tuesday',   8, 1, 1, 'R101'),
(1, 'Tuesday',   9, 2, 2, 'R101'),
-- Wednesday
(1, 'Wednesday', 1, 3, 3, 'Lab1'),
(1, 'Wednesday', 2, 1, 1, 'R101'),
(1, 'Wednesday', 3, 2, 2, 'R101'),
(1, 'Wednesday', 5, 3, 3, 'Lab1'),
(1, 'Wednesday', 6, 1, 1, 'R101'),
(1, 'Wednesday', 8, 2, 2, 'R101'),
(1, 'Wednesday', 9, 3, 3, 'Lab1'),
-- Thursday
(1, 'Thursday',  1, 1, 1, 'R101'),
(1, 'Thursday',  2, 2, 2, 'R101'),
(1, 'Thursday',  3, 3, 3, 'Lab1'),
(1, 'Thursday',  5, 1, 1, 'R101'),
(1, 'Thursday',  6, 2, 2, 'R101'),
(1, 'Thursday',  8, 3, 3, 'Lab1'),
(1, 'Thursday',  9, 1, 1, 'R101'),
-- Friday
(1, 'Friday',    1, 2, 2, 'R101'),
(1, 'Friday',    2, 3, 3, 'Lab1'),
(1, 'Friday',    3, 1, 1, 'R101'),
(1, 'Friday',    5, 2, 2, 'R101'),
(1, 'Friday',    6, 3, 3, 'Lab1'),
(1, 'Friday',    8, 1, 1, 'R101'),
(1, 'Friday',    9, 2, 2, 'R101');
