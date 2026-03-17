import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import query
from werkzeug.security import generate_password_hash

def fix_db():
    try:
        print(">>> DB FIX: Starting correction script...")
        
        # 1. Generate a new, valid hash for 'admin123'
        new_hash = generate_password_hash('admin123')
        print(f">>> Generated new hash: {new_hash}")
        
        # 2. Update ADM001
        res = query("UPDATE users SET password_hash = %s, is_active = 1 WHERE username = 'ADM001'", (new_hash,), commit=True)
        print(f">>> Updated ADM001: {res}")
        
        # 3. Update admin
        res = query("UPDATE users SET password_hash = %s, is_active = 1 WHERE username = 'admin'", (new_hash,), commit=True)
        print(f">>> Updated admin: {res}")
        
        print(">>> DB FIX: Successfully corrected credentials.")
        
    except Exception as e:
        print(f">>> DB FIX ERROR: {e}")

if __name__ == "__main__":
    fix_db()
