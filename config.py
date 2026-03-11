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
    SECRET_KEY = os.getenv("SECRET_KEY", "school-portal-dev-secret-key-2026")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    # Secure Cookies
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── MySQL ─────────────────────────────────────────────
    # Priority: MYSQL_URL > individual vars
    DATABASE_URL = os.getenv("MYSQL_PUBLIC_URL") or os.getenv("MYSQL_URL") or os.getenv("MYSQLURL") or os.getenv("MYSQL_PRIVATE_URL") or os.getenv("DATABASE_URL")
    
    if DATABASE_URL and DATABASE_URL.startswith("mysql"):
        import urllib.parse
        url = urllib.parse.urlparse(DATABASE_URL)
        MYSQL_HOST = url.hostname
        MYSQL_PORT = url.port or 3306
        MYSQL_USER = url.username
        MYSQL_PASSWORD = url.password
        MYSQL_DATABASE = url.path.lstrip('/') if (url.path and len(url.path) > 1) else os.getenv("MYSQLDATABASE", "school_portal")
        MYSQL_SSL_DISABLED = False
    else:
        MYSQL_HOST = os.getenv("MYSQLHOST") or os.getenv("MYSQL_HOST") or ""
        try:
            MYSQL_PORT = int(os.getenv("MYSQLPORT") or os.getenv("MYSQL_PORT") or "3306")
        except (ValueError, TypeError):
            MYSQL_PORT = 3306
        MYSQL_USER = os.getenv("MYSQLUSER") or os.getenv("MYSQL_USER") or "root"
        MYSQL_PASSWORD = os.getenv("MYSQLPASSWORD") or os.getenv("MYSQL_PASSWORD") or ""
        MYSQL_DATABASE = os.getenv("MYSQLDATABASE") or os.getenv("MYSQL_DATABASE") or "school_portal"
        MYSQL_SSL_DISABLED = os.getenv("FLASK_ENV") != "production" and not os.getenv("RAILWAY_ENVIRONMENT")

    # ── File Uploads ────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB limit
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "png", "jpg", "jpeg", "gif"}

    # ── S3 / Railway Bucket ───────────────────────────────────
    S3_KEY = os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID") or os.getenv("S3_KEY")
    S3_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY") or os.getenv("SECRET_ACCESS_KEY") or os.getenv("S3_SECRET")
    S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME") or os.getenv("S3_BUCKET_NAME") or os.getenv("AWS_BUCKET_NAME") or os.getenv("BUCKET_NAME") or os.getenv("BUCKET") or "school-images"
    S3_REGION = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION") or os.getenv("REGION") or "auto"
    S3_ENDPOINT = os.getenv("AWS_ENDPOINT_URL") or os.getenv("AWS_ENDPOINT_URL_S3") or os.getenv("ENDPOINT") or os.getenv("BUCKET_ENDPOINT")
    
    _use_bucket = os.getenv("USE_BUCKET", "false").lower() == "true"
    STORAGE_TYPE = "s3" if _use_bucket else os.getenv("STORAGE_TYPE", "local")
