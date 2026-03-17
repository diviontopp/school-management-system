from database.connection import query

def check_records():
    print("--- User Records ---")
    users = query("SELECT id, username, role FROM users", fetch_all=True)
    for u in users:
        print(u)
        
    print("\n--- Student Records ---")
    students = query("SELECT id, user_id, admission_number, first_name FROM students", fetch_all=True)
    for s in students:
        print(s)

if __name__ == "__main__":
    check_records()
