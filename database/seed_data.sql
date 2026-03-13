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
INSERT IGNORE INTO users (role, username, password_hash) VALUES
('admin', 'admin', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe');

-- ── Users: Teachers ────────────────────────────────────────
INSERT IGNORE INTO users (role, username, password_hash) VALUES
('teacher', 'T001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('teacher', 'T002', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('teacher', 'T003', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe');

-- ── Teachers ───────────────────────────────────────────────
-- user_id 2 = T001, 3 = T002, 4 = T003
INSERT IGNORE INTO teachers (user_id, employee_id, first_name, last_name, department, email, qualification) VALUES
(2, 'T001', 'Priya',    'Sharma',  'Mathematics', 'priya.sharma@school.edu',  'M.Sc Mathematics'),
(3, 'T002', 'Rohit',    'Verma',   'English',     'rohit.verma@school.edu',   'M.A. English'),
(4, 'T003', 'Ananya',   'Singh',   'Science',     'ananya.singh@school.edu',  'M.Sc Physics');

-- ── Users: Students ────────────────────────────────────────
-- password = birthdate DDMMYYYY (bcrypt of 01012010 etc.)
-- Using same hash for demo — real passwords set when students are created
INSERT IGNORE INTO users (role, username, password_hash) VALUES
('student', 'ADM001', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('student', 'ADM002', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe'),
('student', 'ADM003', 'pbkdf2:sha256:600000$PBWQYYPxKtBpWBIS$46b947e3d004309dd64af6c8f0565794bd54acae20f4981a5ce9b30ce48929fe');

-- ── Students ───────────────────────────────────────────────
-- user_id 5 = ADM001, 6 = ADM002, 7 = ADM003
INSERT IGNORE INTO students (user_id, admission_number, first_name, last_name, date_of_birth, gender, class_id, roll_number, email) VALUES
(5, 'ADM001', 'Meera',   'Patel', '2010-01-15', 'F', 1, 1, 'meera.patel@student.school.edu'),
(6, 'ADM002', 'Arjun',   'Kumar', '2010-03-22', 'M', 1, 2, 'arjun.kumar@student.school.edu'),
(7, 'ADM003', 'Shruti',  'Nair',  '2010-07-08', 'F', 2, 1, 'shruti.nair@student.school.edu');

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
