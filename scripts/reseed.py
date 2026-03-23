import os
import sys

# Inject MYSQL local defaults to bypass Railway/env crash when run standalone
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_USER"] = "root"
os.environ["MYSQL_DATABASE"] = "school_portal"
os.environ["MYSQL_PASSWORD"] = ""

# Add project root to python path to import config and database
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database.connection import query

def execute():
    # 1. Clear existing duplicate homework and tests
    query("DELETE FROM homework_submissions", commit=True)
    query("DELETE FROM homework", commit=True)
    query("DELETE FROM test_scores", commit=True)
    query("DELETE FROM tests", commit=True)
    print("Cleared existing homework and tests to remove duplicates.")

    # Get some subjects and classes
    math_id = query("SELECT id FROM subjects WHERE code='MATH'", fetch_one=True)['id']
    eng_id = query("SELECT id FROM subjects WHERE code='ENG'", fetch_one=True)['id']
    sci_id = query("SELECT id FROM subjects WHERE code='SCI'", fetch_one=True)['id']
    
    class_id = query("SELECT id FROM classes WHERE name='10-A'", fetch_one=True)['id']
    teacher_id = 1

    # 2. Insert diverse unique homework
    query(
        """INSERT INTO homework (title, description, subject_id, class_id, assigned_by, assigned_date, deadline)
           VALUES 
           ('Math practice set 5', 'Complete all questions.', %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 0 DAY)),
           ('Chapter 3 essay outline', 'Draft the initial outline.', %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 DAY)),
           ('Physics lab report prep', 'Read the materials before lab.', %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 2 DAY)),
           ('Algebra worksheet 12', 'Solve equations.', %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 3 DAY))
        """,
        (math_id, class_id, teacher_id, eng_id, class_id, teacher_id, sci_id, class_id, teacher_id, math_id, class_id, teacher_id),
        commit=True
    )
    print("Inserted fresh unique homework data.")

    # 3. Insert diverse unique tests
    query(
        """INSERT INTO tests (name, subject_id, class_id, test_date, max_marks, portions, test_type, created_by)
           VALUES 
           ('Mid-Term Exam', %s, %s, DATE_ADD(CURDATE(), INTERVAL 7 DAY), 100, 'Chapters 1-5', 'MID TERM', %s),
           ('Weekly Quiz', %s, %s, DATE_ADD(CURDATE(), INTERVAL 2 DAY), 20, 'Mechanics', 'QUIZ', %s)
        """,
        (eng_id, class_id, teacher_id, sci_id, class_id, teacher_id),
        commit=True
    )
    print("Inserted fresh unique test data.")

if __name__ == "__main__":
    execute()
