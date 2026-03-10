import os
from database.connection import execute_script
from config import Config

def initialize_database():
    print(f"--- DATABASE INITIALIZATION STARTED ---")
    print(f"Target Host: {Config.MYSQL_HOST}")
    print(f"Target DB: {Config.MYSQL_DATABASE}")
    
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    seed_path = os.path.join(os.path.dirname(__file__), 'database', 'seed_data.sql')
    
    try:
        # 1. Execute Schema
        if os.path.exists(schema_path):
            print(f"Executing schema from {schema_path}...")
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                execute_script(schema_sql)
            print("✓ Schema initialized successfully.")
        else:
            print("✗ schema.sql not found!")

        # 2. Execute Basic Seed Data
        if os.getenv("SEED_DB", "True") == "True" and os.path.exists(seed_path):
            print(f"Executing seed data from {seed_path}...")
            with open(seed_path, 'r', encoding='utf-8') as f:
                seed_sql = f.read()
                execute_script(seed_sql)
            print("✓ Seed data loaded successfully.")

        print("--- DATABASE INITIALIZATION COMPLETED ---")
    except Exception as e:
        print(f"✗ ERROR during initialization: {e}")

if __name__ == "__main__":
    initialize_database()
