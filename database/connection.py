import mysql.connector
from mysql.connector import pooling
import os
from config import Config


# ── Connection pool ────────────────────────────────────────────────────────
_pool = None
_pool_error = None  # Store any connection error so routes can report it


def get_pool():
    global _pool, _pool_error
    if _pool is not None:
        return _pool
    if _pool_error is not None:
        raise _pool_error

    # Only attempt connection if host is configured
    if not Config.MYSQL_HOST:
        _pool_error = Exception("DATABASE_URL is not configured. Please set it in Hugging Face Space secrets.")
        raise _pool_error

    try:
        print(f"DEBUG: Attempting to connect to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}...")
        kwargs = {
            "pool_name": "school_portal_pool",
            "pool_size": 5,
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DATABASE,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "connection_timeout": 10,   # 10-second timeout — prevents hanging
        }
        if Config.DATABASE_URL and "ssl-mode=" in Config.DATABASE_URL:
            # If the URL already contains ssl-mode, the connector might handle it,
            # but we ensure the pooling kwargs are consistent.
            pass

        if not getattr(Config, 'MYSQL_SSL_DISABLED', True):
            # Aiven and most cloud providers require SSL. 
            # We use 'REQUIRED' or 'VERIFY_IDENTITY' usually, but 'ssl_disabled=False' 
            # is the basic toggle in mysql-connector-python.
            kwargs['ssl_disabled'] = False
            # For Aiven specifically, they often provide a CA cert. 
            # If the user hasn't provided one, we at least enable SSL.
            # We don't verify cert here to avoid path issues in container, 
            # unless a CA path is explicitly set in env (future proofing).
            ca_path = os.getenv("MYSQL_ATTR_SSL_CA")
            if ca_path and os.path.exists(ca_path):
                kwargs['ssl_ca'] = ca_path
                kwargs['ssl_verify_cert'] = True
            else:
                kwargs['ssl_verify_identity'] = False
                kwargs['ssl_verify_cert'] = False

        _pool = pooling.MySQLConnectionPool(**kwargs)
        return _pool
    except Exception as e:
        _pool_error = e
        raise


def get_connection():
    """Return a connection from the pool."""
    return get_pool().get_connection()


def query(sql, params=None, fetch_one=False, fetch_all=True, commit=False):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_script(sql_script):
    """Run a multi-statement SQL script (used for schema setup)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        for statement in sql_script.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def initialize_database():
    """Run schema.sql and seed_data.sql if INIT_DB=True."""
    print(f"--- DATABASE INITIALIZATION TRIGGERED ---", flush=True)
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(base_dir, 'database', 'schema.sql')
    seed_path = os.path.join(base_dir, 'database', 'seed_data.sql')
    
    def process_and_execute(file_path, label):
        if not os.path.exists(file_path):
            print(f"✗ {label} not found at {file_path}!", flush=True)
            return

        print(f"Executing {label} from {file_path}...", flush=True)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Strip CREATE DATABASE and USE commands to ensure it uses the Railway DB
        cleaned_lines = []
        for line in lines:
            trimmed = line.strip().upper()
            if trimmed.startswith("CREATE DATABASE") or trimmed.startswith("USE "):
                print(f"  [Skipping DB Command]: {line.strip()}", flush=True)
                continue
            cleaned_lines.append(line)
        
        try:
            execute_script("".join(cleaned_lines))
            print(f"✓ {label} initialized successfully.", flush=True)
        except Exception as e:
            print(f"✗ ERROR executing {label}: {e}", flush=True)

    try:
        # 1. Execute Schema
        process_and_execute(schema_path, "Schema")

        # 2. Execute Seed Data
        if os.getenv("SEED_DB", "True") == "True":
            process_and_execute(seed_path, "Seed Data")

        print("--- DATABASE INITIALIZATION COMPLETED ---", flush=True)
    except Exception as e:
        print(f"✗ CRITICAL ERROR during initialization: {e}", flush=True)
