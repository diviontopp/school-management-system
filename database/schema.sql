-- ============================================================
-- School Portal — Full Database Schema
-- Engine: MySQL 8.0+ | Charset: utf8mb4
-- Run: mysql -u root -p < database/schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS school_portal
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE school_portal;

-- ============================================================
-- 1. USERS & AUTHENTICATION
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    role        ENUM('student','teacher','parent','admin') NOT NULL,
    username    VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 2. ACADEMIC STRUCTURE
-- ============================================================

CREATE TABLE IF NOT EXISTS classes (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(20) NOT NULL,        -- e.g. "10-A"
    grade          INT         NOT NULL,         -- e.g. 10
    section        VARCHAR(5)  NOT NULL,         -- e.g. "A"
    academic_year  VARCHAR(9)  NOT NULL          -- e.g. "2025-2026"
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS subjects (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    code  VARCHAR(20)  NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 3. TEACHERS (declared before class_subjects)
-- ============================================================

CREATE TABLE IF NOT EXISTS teachers (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT         NOT NULL UNIQUE,
    employee_id   VARCHAR(20) NOT NULL UNIQUE,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    department    VARCHAR(100),
    phone         VARCHAR(15),
    email         VARCHAR(100),
    qualification VARCHAR(200),
    photo_url     VARCHAR(255),
    join_date     DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 4. CLASS ↔ SUBJECT ↔ TEACHER
-- ============================================================

CREATE TABLE IF NOT EXISTS class_subjects (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    class_id    INT NOT NULL,
    subject_id  INT NOT NULL,
    teacher_id  INT,
    FOREIGN KEY (class_id)   REFERENCES classes(id)   ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)  ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)  ON DELETE SET NULL,
    UNIQUE KEY uq_class_subject (class_id, subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 5. STUDENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS students (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    user_id          INT         NOT NULL UNIQUE,
    admission_number VARCHAR(20) NOT NULL UNIQUE,
    first_name       VARCHAR(50) NOT NULL,
    last_name        VARCHAR(50) NOT NULL,
    date_of_birth    DATE        NOT NULL,
    gender           ENUM('M','F','Other') NOT NULL,
    class_id         INT         NOT NULL,
    roll_number      INT,
    phone            VARCHAR(15),
    email            VARCHAR(100),
    address          TEXT,
    photo_url        VARCHAR(255),
    admission_date   DATE,
    FOREIGN KEY (user_id)   REFERENCES users(id)   ON DELETE CASCADE,
    FOREIGN KEY (class_id)  REFERENCES classes(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 6. PARENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS parents (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT         NOT NULL UNIQUE,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    phone         VARCHAR(15),
    email         VARCHAR(100),
    relationship  ENUM('Father','Mother','Guardian') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS parent_student (
    parent_id  INT NOT NULL,
    student_id INT NOT NULL,
    PRIMARY KEY (parent_id, student_id),
    FOREIGN KEY (parent_id)  REFERENCES parents(id)  ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 7. STUDENT ATTENDANCE
-- ============================================================

CREATE TABLE IF NOT EXISTS student_attendance (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT  NOT NULL,
    date       DATE NOT NULL,
    status     ENUM('Present','Absent','Late','Excused') NOT NULL,
    marked_by  INT  NOT NULL,
    marked_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_date (student_id, date),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by)  REFERENCES teachers(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 8. TEACHER ATTENDANCE
-- ============================================================

CREATE TABLE IF NOT EXISTS teacher_attendance (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id   INT  NOT NULL,
    date         DATE NOT NULL,
    status       ENUM('Present','Absent','On Leave','Late') NOT NULL,
    check_in_time TIME,
    remarks      VARCHAR(255),
    UNIQUE KEY uq_teacher_date (teacher_id, date),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 9. TESTS & GRADES
-- ============================================================

CREATE TABLE IF NOT EXISTS tests (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    subject_id  INT NOT NULL,
    class_id    INT NOT NULL,
    test_date   DATE NOT NULL,
    max_marks   INT  NOT NULL,
    portions    TEXT,
    test_type   ENUM('Unit Test','Mid Term','Final','Quiz','Assignment') NOT NULL,
    created_by  INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)  ON DELETE RESTRICT,
    FOREIGN KEY (class_id)   REFERENCES classes(id)   ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES teachers(id)  ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS test_scores (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    test_id         INT           NOT NULL,
    student_id      INT           NOT NULL,
    marks_obtained  DECIMAL(5,2),
    grade           VARCHAR(5),
    remarks         VARCHAR(255),
    updated_by      INT           NOT NULL,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_test_student (test_id, student_id),
    FOREIGN KEY (test_id)    REFERENCES tests(id)    ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by) REFERENCES teachers(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 10. HOMEWORK
-- ============================================================

CREATE TABLE IF NOT EXISTS homework (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    title          VARCHAR(200) NOT NULL,
    description    TEXT,
    subject_id     INT  NOT NULL,
    class_id       INT  NOT NULL,
    assigned_by    INT  NOT NULL,
    assigned_date  DATE NOT NULL,
    deadline       DATE NOT NULL,
    attachment_url VARCHAR(255),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id)  REFERENCES subjects(id)  ON DELETE RESTRICT,
    FOREIGN KEY (class_id)    REFERENCES classes(id)   ON DELETE RESTRICT,
    FOREIGN KEY (assigned_by) REFERENCES teachers(id)  ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS homework_submissions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    homework_id     INT NOT NULL,
    student_id      INT NOT NULL,
    submission_file VARCHAR(255),
    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status          ENUM('Submitted','Late','Not Submitted') DEFAULT 'Submitted',
    grade           VARCHAR(10),
    feedback        TEXT,
    UNIQUE KEY uq_hw_student (homework_id, student_id),
    FOREIGN KEY (homework_id) REFERENCES homework(id)  ON DELETE CASCADE,
    FOREIGN KEY (student_id)  REFERENCES students(id)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 11. TIMETABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS periods (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    period_number INT  NOT NULL,
    start_time    TIME NOT NULL,
    end_time      TIME NOT NULL,
    is_break      BOOLEAN DEFAULT FALSE,
    break_name    VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS class_timetable (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    class_id     INT NOT NULL,
    day_of_week  ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') NOT NULL,
    period_id    INT NOT NULL,
    subject_id   INT,
    teacher_id   INT,
    room         VARCHAR(20),
    UNIQUE KEY uq_timetable_slot (class_id, day_of_week, period_id),
    FOREIGN KEY (class_id)   REFERENCES classes(id)   ON DELETE CASCADE,
    FOREIGN KEY (period_id)  REFERENCES periods(id)   ON DELETE RESTRICT,
    FOREIGN KEY (subject_id) REFERENCES subjects(id)  ON DELETE SET NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)  ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 12. TEACHER SUBSTITUTION
-- ============================================================

CREATE TABLE IF NOT EXISTS teacher_leave (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id  INT NOT NULL,
    leave_date  DATE NOT NULL,
    reason      VARCHAR(255),
    status      ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    approved_by INT,
    FOREIGN KEY (teacher_id)  REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id)    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS substitutions (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    leave_id              INT NOT NULL,
    original_teacher_id   INT NOT NULL,
    substitute_teacher_id INT NOT NULL,
    class_id              INT NOT NULL,
    period_id             INT NOT NULL,
    date                  DATE NOT NULL,
    day_of_week           VARCHAR(10) NOT NULL,
    status                ENUM('Proposed','Approved','Rejected') DEFAULT 'Proposed',
    approved_by           INT,
    FOREIGN KEY (leave_id)              REFERENCES teacher_leave(id) ON DELETE CASCADE,
    FOREIGN KEY (original_teacher_id)   REFERENCES teachers(id)      ON DELETE RESTRICT,
    FOREIGN KEY (substitute_teacher_id) REFERENCES teachers(id)      ON DELETE RESTRICT,
    FOREIGN KEY (class_id)              REFERENCES classes(id)       ON DELETE RESTRICT,
    FOREIGN KEY (period_id)             REFERENCES periods(id)       ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 13. STUDENT REMARKS
-- ============================================================

CREATE TABLE IF NOT EXISTS student_remarks (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    student_id           INT  NOT NULL,
    teacher_id           INT  NOT NULL,
    remark               TEXT NOT NULL,
    remark_type          ENUM('Academic','Behavioral','Appreciation','General') NOT NULL,
    date                 DATE NOT NULL,
    is_visible_to_parent BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 14. LIBRARY MANAGEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS books (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    title            VARCHAR(200) NOT NULL,
    author           VARCHAR(200) NOT NULL,
    isbn             VARCHAR(20)  UNIQUE,
    publisher        VARCHAR(100),
    category         VARCHAR(50),
    total_copies     INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    shelf_location   VARCHAR(20),
    cover_image_url  VARCHAR(255),
    description      TEXT,
    added_date       DATE,
    is_recommended   BOOLEAN DEFAULT FALSE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS library_members (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    member_type     ENUM('Student','Teacher','Staff') NOT NULL,
    membership_date DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    max_books       INT DEFAULT 3,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS borrowings (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT            NOT NULL,
    member_id    INT            NOT NULL,
    borrow_date  DATE           NOT NULL,
    due_date     DATE           NOT NULL,
    return_date  DATE,
    fine_amount  DECIMAL(10,2)  DEFAULT 0.00,
    status       ENUM('Borrowed','Returned','Overdue') DEFAULT 'Borrowed',
    FOREIGN KEY (book_id)   REFERENCES books(id)            ON DELETE RESTRICT,
    FOREIGN KEY (member_id) REFERENCES library_members(id)  ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 15. CLUBS & EVENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS clubs (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(100) NOT NULL,
    description       TEXT,
    category          VARCHAR(50),
    logo_url          VARCHAR(255),
    lead_student_id   INT,
    faculty_advisor_id INT,
    max_members       INT,
    is_active         BOOLEAN DEFAULT TRUE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_student_id)    REFERENCES students(id) ON DELETE SET NULL,
    FOREIGN KEY (faculty_advisor_id) REFERENCES teachers(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS club_members (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    club_id      INT NOT NULL,
    student_id   INT NOT NULL,
    joined_date  DATE,
    role         ENUM('Member','Lead','Co-Lead') DEFAULT 'Member',
    is_active    BOOLEAN DEFAULT TRUE,
    UNIQUE KEY uq_club_student (club_id, student_id),
    FOREIGN KEY (club_id)    REFERENCES clubs(id)    ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS events (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    club_id               INT          NOT NULL,
    name                  VARCHAR(200) NOT NULL,
    description           TEXT,
    event_date            DATETIME     NOT NULL,
    venue                 VARCHAR(100),
    max_participants      INT,
    registration_deadline DATE,
    poster_url            VARCHAR(255),
    is_active             BOOLEAN DEFAULT TRUE,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS event_rsvps (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    event_id              INT NOT NULL,
    student_id            INT NOT NULL,
    rsvp_date             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status                ENUM('Registered','Attended','Absent') DEFAULT 'Registered',
    certificate_generated BOOLEAN DEFAULT FALSE,
    UNIQUE KEY uq_rsvp (event_id, student_id),
    FOREIGN KEY (event_id)   REFERENCES events(id)   ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS club_announcements (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    club_id     INT          NOT NULL,
    title       VARCHAR(200) NOT NULL,
    content     TEXT         NOT NULL,
    posted_by   INT          NOT NULL,
    attachment_url VARCHAR(255),
    posted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id)   REFERENCES clubs(id)    ON DELETE CASCADE,
    FOREIGN KEY (posted_by) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS event_photos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    event_id    INT          NOT NULL,
    photo_url   VARCHAR(255) NOT NULL,
    caption     VARCHAR(200),
    uploaded_by INT          NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id)    REFERENCES events(id)   ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 16. PUBLIC ENQUIRIES
-- ============================================================

CREATE TABLE IF NOT EXISTS enquiries (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    parent_name  VARCHAR(100) NOT NULL,
    email        VARCHAR(100) NOT NULL,
    phone        VARCHAR(15),
    child_grade  VARCHAR(20),
    message      TEXT,
    status       ENUM('New','Contacted','Enrolled','Closed') DEFAULT 'New',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 17. SCHOOL NOTICES (Samvaad Hub)
-- ============================================================

CREATE TABLE IF NOT EXISTS notices (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    content     TEXT         NOT NULL,
    posted_by   INT          NOT NULL,
    posted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active   BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (posted_by) REFERENCES teachers(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
