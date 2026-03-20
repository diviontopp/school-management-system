print(">>> BOOT: app.py is starting imports...", flush=True)
import os
import sys
from flask import Flask, render_template, request, send_from_directory
from config import Config
print(f">>> BOOT: Config loaded. MYSQL_HOST={'set' if Config.MYSQL_HOST else 'None'}...", flush=True)
# Talisman removed for now to simplify boot debugging
from database.connection import initialize_database

from werkzeug.middleware.proxy_fix import ProxyFix
from whitenoise import WhiteNoise

def create_app():
    print(">>> [BOOT] Initializing Flask Application...", flush=True)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'),
                static_url_path='/static')
    
    app.config.from_object(Config)

    # ── Database Pre-flight ─────────────────────────────────
    if os.getenv("INIT_DB", "False").lower() == "true":
        print(">>> [BOOT] Database initialization requested via INIT_DB=True", flush=True)
        try:
            from database.connection import initialize_database
            initialize_database()
            print(">>> [BOOT] Database initialization successful.", flush=True)
        except Exception as e:
            print(f">>> [BOOT] DATABASE INIT ERROR (Non-fatal for app boot): {e}", flush=True)

    # ── Blueprint Registration ──────────────────────────────
    print(">>> [BOOT] Registering route blueprints...", flush=True)
    try:
        from routes.public import public_bp
        from routes.auth import auth_bp
        from routes.student import student_bp
        from routes.teacher import teacher_bp
        from routes.parent import parent_bp
        from routes.admin import admin_bp
        from routes.library import library_bp
        from routes.clubs import clubs_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(student_bp, url_prefix='/student')
        app.register_blueprint(teacher_bp, url_prefix='/teacher')
        app.register_blueprint(parent_bp, url_prefix='/parent')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(library_bp, url_prefix='/library')
        app.register_blueprint(clubs_bp, url_prefix='/clubs')
        print(">>> [BOOT] All blueprints registered successfully.", flush=True)
    except Exception as e:
        print(f">>> [BOOT] CRITICAL ERROR registering blueprints: {e}", flush=True)
        # We don't raise here yet to allow error handler to catch it if possible

    # ── Middleware ──────────────────────────────────────────
    static_dir = os.path.abspath(app.static_folder)
    print(f">>> [BOOT] Configuring WhiteNoise for: {static_dir}", flush=True)
    app.wsgi_app = WhiteNoise(app.wsgi_app, 
                             root=static_dir, 
                             prefix='/static/',
                             index_file=True)
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    @app.before_request
    def log_request_info():
        # High-level log for every request
        print(f">>> [REQ] {request.method} {request.path}", flush=True)

    # ── Fail-safe Routes ──────────────────────────────────
    @app.route('/health')
    def health():
        from database.connection import query
        db_status = "unknown"
        try:
            query("SELECT 1", fetch_one=True)
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        return {"status": "ok", "env": os.getenv("FLASK_ENV", "dev"), "database": db_status}, 200

    # ── Error Handling ─────────────────────────────────────
    from werkzeug.exceptions import HTTPException
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
            
        import traceback
        err_msg = str(e)
        trace = traceback.format_exc()
        
        # Log the full stack trace for Railway
        print("="*60, flush=True)
        print(f">>> CRITICAL 500 ERROR: {err_msg}", flush=True)
        print(trace, flush=True)
        print("="*60, flush=True)
        
        # Return a slightly more helpful 500 in dev or if specific info exists
        # But for security in production, keep it generic unless authorized
        return render_template('public/base.html'), 500 # Fallback to a base template if possible

    # ── Template Utilities ────────────────────────────────
    from utils.storage import get_storage_url
    @app.context_processor
    def inject_storage():
        return dict(storage_url=get_storage_url)

    @app.template_filter('format_time')
    def format_time_filter(td):
        if td is None: return ''
        try:
            total_seconds = int(td.total_seconds())
            hours, minutes = total_seconds // 3600, (total_seconds % 3600) // 60
            return f"{hours:02d}:{minutes:02d}"
        except:
            return str(td)

    print(">>> [BOOT] App creation complete.", flush=True)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=os.getenv('PORT', 5000))
