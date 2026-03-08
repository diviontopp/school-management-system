import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Flask ─────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "school-portal-dev-secret-key-2026") # In prod, this must be a heavy random string
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    # Secure Cookies
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── MySQL ─────────────────────────────────────────────
    # Standard connection string fallback (e.g. for Render + Aiven URL)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("mysql"):
        import urllib.parse
        url = urllib.parse.urlparse(DATABASE_URL)
        MYSQL_HOST = url.hostname
        MYSQL_PORT = url.port or 3306
        MYSQL_USER = url.username
        MYSQL_PASSWORD = url.password
        MYSQL_DATABASE = url.path[1:] if url.path else "defaultdb"
        MYSQL_SSL_DISABLED = False
    else:
        # No DATABASE_URL set — leave host empty so connection.py fails fast
        # instead of trying localhost (which hangs the gunicorn worker)
        MYSQL_HOST = os.getenv("MYSQL_HOST", "")  # Empty = no DB configured
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        MYSQL_USER = os.getenv("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "school_portal")
        MYSQL_SSL_DISABLED = True

    # ── File Uploads ────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB limit
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg", "jpeg", "gif"}
