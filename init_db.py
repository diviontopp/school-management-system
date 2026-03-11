import os
import sys

# DEBUG: Force immediate flushing of all output
print(">>> BOOT: init_db.py is starting...", flush=True)

# Ensure current directory is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import initialize_database

if __name__ == "__main__":
    print(">>> Starting Database Initialization Script...")
    if os.getenv("INIT_DB", "False") == "True":
        try:
            initialize_database()
            print(">>> Database Initialization Successful.")
        except Exception as e:
            print(f">>> Database Initialization Failed: {e}")
            # We don't exit 1 here because we want the app to try and boot anyway
            # unless it's a critical schema failure.
    else:
        print(">>> INIT_DB is False, skipping initialization.")
