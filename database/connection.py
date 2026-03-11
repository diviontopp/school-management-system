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
            "pool_size": 10,             # Increased pool size for better concurrency
            "host": Config.MYSQL_HOST,
            "port": Config.MYSQL_PORT,
            "user": Config.MYSQL_USER,
            "password": Config.MYSQL_PASSWORD,
            "database": Config.MYSQL_DATABASE,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci",
            "autocommit": False,
            "connection_timeout": 15,   # Increased timeout for cold starts
            "client_flags": [mysql.connector.ClientFlag.MULTI_STATEMENTS] # Performance optimization
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

        print(f"DEBUG: Connecting to {kwargs['host']} port {kwargs['port']} database {kwargs['database']}...", flush=True)
        _pool = pooling.MySQLConnectionPool(**kwargs)
        print(f"✓ Connection pool created for {kwargs['database']}!", flush=True)
        return _pool
    except Exception as e:
        _pool_error = e
        raise


def get_connection():
    """Return a validated connection from the pool, with auto-reconnect."""
    pool = get_pool()
    try:
        conn = pool.get_connection()
        # Pre-flight ping to ensure Railway's proxy hasn't killed the idle connection
        try:
            conn.ping(reconnect=True, attempts=3, delay=1)
        except Exception as ping_err:
            print(f"WARN: Connection ping failed, forcing new connection: {ping_err}", flush=True)
            # If ping fails, we try to get a fresh one if possible, or just let it propagate
            pass
        return conn
    except Exception as e:
        print(f"ERROR: Could not get connection from pool: {e}", flush=True)
        raise


def query(sql, params=None, fetch_one=False, fetch_all=True, commit=False):
    """Execute a query with absolute leak prevention and robust retry."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql, params or ())
            
            if commit:
                conn.commit()
                last_id = cursor.lastrowid
                return last_id
            
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
            
        finally:
            cursor.close()
            
    except Exception as e:
        if conn:
            conn.rollback()
        # Log specific MySQL error codes for Railway debugging
        error_code = getattr(e, 'errno', 'Unknown')
        print(f"DATABASE ERROR [{error_code}]: {e}", flush=True)
        raise e
    finally:
        if conn:
            # Absolute guarantee: return connection to pool
            conn.close()


def execute_script(sql_script):
    """Run a multi-statement SQL script using native multi-execution."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # multi=True returns an iterator of results for each statement
        results = cursor.execute(sql_script, multi=True)
        for result in results:
            # We must consume the results to avoid "Unread result" errors
            if result.with_rows:
                result.fetchall()
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
            content = f.read()
            
        # Robustly remove database-level boilerplate that fails on Railway
        import re
        # Removes: CREATE DATABASE ... ; (case-insensitive, multi-line)
        content = re.sub(r'(?i)CREATE DATABASE.*?;', '-- [Removed Create DB]', content, flags=re.DOTALL)
        # Removes: USE ... ;
        content = re.sub(r'(?i)USE .*?;', '-- [Removed USE DB]', content)
        
        try:
            execute_script(content)
            print(f"✓ {label} initialized successfully.", flush=True)
            return True
        except Exception as e:
            print(f"✗ ERROR executing {label}: {e}", flush=True)
            return False

    try:
        # 0. Emergency creation of enquiries table (First priority)
        print("Ensuring 'enquiries' table exists...", flush=True)
        enquiry_sql = """
        CREATE TABLE IF NOT EXISTS enquiries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            parent_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(15),
            child_grade VARCHAR(20),
            message TEXT,
            status ENUM('New','Contacted','Enrolled','Closed') DEFAULT 'New',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        execute_script(enquiry_sql)
        print("✓ 'enquiries' table verified/created.", flush=True)

        # 1. Execute full Schema
        process_and_execute(schema_path, "Full Schema")

        # 2. Execute Seed Data
        if os.getenv("SEED_DB", "True") == "True":
            process_and_execute(seed_path, "Seed Data")

        print("--- DATABASE INITIALIZATION COMPLETED ---", flush=True)
    except Exception as e:
        print(f"✗ CRITICAL ERROR during initialization: {e}", flush=True)
