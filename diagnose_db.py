import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import query
from werkzeug.security import generate_password_hash, check_password_hash

def diagnose():
    try:
        print("--- DATABASE DIAGNOSTIC START ---")
        
        # 1. Check users table
        users = query("SELECT id, username, role, password_hash FROM users WHERE username = 'ADM001'", fetch_all=True)
        if not users:
            print("❌ User ADM001 not found in database!")
        else:
            for user in users:
                phash = user['password_hash']
                print(f"✅ Found user: {user['username']} | Role: {user['role']} | Hash: '{phash}'")
                if not phash:
                    print("⚠️  CRITICAL: Password hash is EMPTY for this user.")
                else:
                    try:
                        # Test if the hash is valid
                        is_valid = check_password_hash(phash, 'admin123')
                        print(f"🔍 Hash check for 'admin123': {is_valid}")
                    except Exception as e:
                        print(f"❌ Hash check error: {e}")

        # 2. Check if we can insert/update
        new_hash = generate_password_hash('admin123')
        print(f"🛠️  Generated new hash for 'admin123': {new_hash}")
        
    except Exception as e:
        print(f"💥 Diagnostic failed: {e}")

if __name__ == "__main__":
    diagnose()
