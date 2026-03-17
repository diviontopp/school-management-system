-- ============================================================
-- School Portal — Seed Data for Testing
-- Run AFTER schema.sql
-- ============================================================

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
-- password: admin123 
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
INSERT IGNORE INTO teachers (user_id, employee_id, first_name, last_name, department, email, qualification)
SELECT id, 'T001', 'Priya', 'Sharma', 'Mathematics', 'priya.sharma@school.edu', 'M.Sc Mathematics' FROM users WHERE username = 'T001';

INSERT IGNORE INTO teachers (user_id, employee_id, first_name, last_name, department, email, qualification)
SELECT id, 'T002', 'Rohit', 'Verma', 'English', 'rohit.verma@school.edu', 'M.A. English' FROM users WHERE username = 'T002';

INSERT IGNORE INTO teachers (user_id, employee_id, first_name, last_name, department, email, qualification)
SELECT id, 'T003', 'Ananya', 'Singh', 'Science', 'ananya.singh@school.edu', 'M.Sc Physics' FROM users WHERE username = 'T003';

-- ── Users: Students ────────────────────────────────────────
INSERT INTO users (role, username, password_hash) VALUES
('student', 'DBX001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('student', 'DBX002', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('student', 'DBX003', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

-- ── Students ───────────────────────────────────────────────
INSERT INTO students (user_id, admission_number, first_name, last_name, date_of_birth, gender, class_id, roll_number, email)
SELECT id, 'DBX001', 'Meera', 'Patel', '2010-01-15', 'F', (SELECT id FROM classes WHERE name='10-A' LIMIT 1), 1, 'meera.patel@student.school.edu' FROM users WHERE username = 'DBX001'
ON DUPLICATE KEY UPDATE user_id = VALUES(user_id), class_id = VALUES(class_id);

INSERT INTO students (user_id, admission_number, first_name, last_name, date_of_birth, gender, class_id, roll_number, email)
SELECT id, 'DBX002', 'Arjun', 'Kumar', '2010-03-22', 'M', (SELECT id FROM classes WHERE name='10-A' LIMIT 1), 2, 'arjun.kumar@student.school.edu' FROM users WHERE username = 'DBX002'
ON DUPLICATE KEY UPDATE user_id = VALUES(user_id), class_id = VALUES(class_id);

INSERT INTO students (user_id, admission_number, first_name, last_name, date_of_birth, gender, class_id, roll_number, email)
SELECT id, 'DBX003', 'Shruti', 'Nair', '2010-07-08', 'F', (SELECT id FROM classes WHERE name='10-B' LIMIT 1), 1, 'shruti.nair@student.school.edu' FROM users WHERE username = 'DBX003'
ON DUPLICATE KEY UPDATE user_id = VALUES(user_id), class_id = VALUES(class_id);

-- ── Users: Parents ─────────────────────────────────────────
INSERT INTO users (role, username, password_hash) VALUES
('parent', 'parent001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe')
ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash);

INSERT IGNORE INTO parents (user_id, first_name, last_name, phone, email, relationship) 
SELECT id, 'Ramesh', 'Patel', '9876543210', 'ramesh.patel@gmail.com', 'Father' FROM users WHERE username = 'parent001';

INSERT IGNORE INTO parent_student (parent_id, student_id) 
SELECT 
    (SELECT id FROM parents WHERE email = 'ramesh.patel@gmail.com' LIMIT 1),
    (SELECT id FROM students WHERE admission_number = 'DBX001' LIMIT 1);

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
INSERT IGNORE INTO class_subjects (class_id, subject_id, teacher_id) 
SELECT 
    (SELECT id FROM classes WHERE name = '10-A' LIMIT 1),
    (SELECT id FROM subjects WHERE code = 'MATH' LIMIT 1),
    (SELECT id FROM teachers WHERE employee_id = 'T001' LIMIT 1);

INSERT IGNORE INTO class_subjects (class_id, subject_id, teacher_id) 
SELECT 
    (SELECT id FROM classes WHERE name = '10-A' LIMIT 1),
    (SELECT id FROM subjects WHERE code = 'ENG' LIMIT 1),
    (SELECT id FROM teachers WHERE employee_id = 'T002' LIMIT 1);

-- ── Tests ────────────────────────────────────────────────
INSERT IGNORE INTO tests (name, subject_id, class_id, test_date, max_marks, portions, test_type, created_by) 
SELECT 'Unit Test 3 - Quadratics', (SELECT id FROM subjects WHERE code='MATH'), (SELECT id FROM classes WHERE name='10-A'), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 25, 'Quadratic equations', 'Unit Test', 1;

-- ── Homework ─────────────────────────────────────────────
INSERT IGNORE INTO homework (title, description, subject_id, class_id, assigned_by, assigned_date, deadline)
SELECT 'Solve Exercise 4.2', 'Complete quadratic equations.', (SELECT id FROM subjects WHERE code='MATH'), (SELECT id FROM classes WHERE name='10-A'), 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 DAY);

-- ── Attendance ───────────────────────────────────────────
-- Use student DBX001
INSERT IGNORE INTO student_attendance (student_id, date, status, marked_by) 
SELECT (SELECT id FROM students WHERE admission_number='DBX001'), DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Present', 1;

INSERT IGNORE INTO student_attendance (student_id, date, status, marked_by) 
SELECT (SELECT id FROM students WHERE admission_number='DBX001'), DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'Present', 1;

INSERT IGNORE INTO student_attendance (student_id, date, status, marked_by) 
SELECT (SELECT id FROM students WHERE admission_number='DBX001'), DATE_SUB(CURDATE(), INTERVAL 3 DAY), 'Absent', 1;
