import os
from dotenv import load_dotenv

load_dotenv() # Load .env first as a base

class Config:
    @staticmethod
    def get_env(key, default=None):
        """Helper to get env var with priority for Railway's naming (no underscores)"""
        # Priority: Railway naming > Standard naming > Default
        railway_key = key.replace("_", "")
        return os.getenv(key) or os.getenv(railway_key) or default
    # ── Flask ─────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "school-portal-dev-secret-key-2026") # In prod, this must be a heavy random string
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    # Secure Cookies
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── MySQL ─────────────────────────────────────────────
    # Railway provides MYSQL_URL automatically if the services are in the same project.
    # This URL contains the correct host, user, password, AND database name.
    DATABASE_URL = os.getenv("MYSQL_PUBLIC_URL") or os.getenv("MYSQL_URL") or os.getenv("MYSQLURL") or os.getenv("MYSQL_PRIVATE_URL") or os.getenv("DATABASE_URL")
    
    if DATABASE_URL and DATABASE_URL.startswith("mysql"):
        import urllib.parse
        url = urllib.parse.urlparse(DATABASE_URL)
        MYSQL_HOST = url.hostname
        MYSQL_PORT = url.port or 3306
        MYSQL_USER = url.username
        MYSQL_PASSWORD = url.password
        # Priority: Railway URL path > Local env > default
        MYSQL_DATABASE = url.path[1:] if (url.path and len(url.path) > 1) else os.getenv("MYSQLDATABASE", "school_portal")
        MYSQL_SSL_DISABLED = False
    else:
        # Fallback to individual variables
        # We prioritize the "Clean" Railway names (no underscores)
        MYSQL_HOST = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST") or ""
        MYSQL_PORT = int(os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306")
        MYSQL_USER = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER") or "root"
        MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD") or ""
        MYSQL_DATABASE = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or "school_portal"
        # Only disable SSL if strictly not in production
        MYSQL_SSL_DISABLED = os.getenv("FLASK_ENV") != "production" and not os.getenv("RAILWAY_ENVIRONMENT")

    # ── File Uploads ────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB limit
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg", "jpeg", "gif"}
