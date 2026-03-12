print(">>> BOOT: app.py is starting imports...", flush=True)
import os
import sys
from flask import Flask, render_template, request
from config import Config
print(f">>> BOOT: Config loaded. MYSQL_HOST={'set' if Config.MYSQL_HOST else 'None'}...", flush=True)
from flask_talisman import Talisman
from database.connection import initialize_database

from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    print(">>> Creating Flask App...", flush=True)
    app = Flask(__name__, 
                template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')),
                static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'static')),
                static_url_path='/static')
    
    # ── Configuration ──────────────────────────────────────
    app.config.from_object(Config)
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # ── Blueprint Registration (Early) ──────────────────────
    from routes.public import public_bp
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.teacher import teacher_bp
    from routes.parent import parent_bp
    from routes.admin import admin_bp
    from routes.library import library_bp
    from routes.clubs import clubs_bp

    # Explicitly register PUBLIC first to ensure / is captured correctly
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(library_bp, url_prefix='/library')
    app.register_blueprint(clubs_bp, url_prefix='/clubs')

    # ── Middleware ──────────────────────────────────────────
    # Trust Railway Edge Proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    # Relaxed Talisman for Railway
    csp = {
        'default-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "*"],
        'img-src': ["'self'", "data:", "https:", "*"]
    }
    Talisman(app, 
             content_security_policy=csp, 
             force_https=False, 
             session_cookie_secure=False
    )

    # ── Logging ───────────────────────────────────────────
    @app.before_request
    def log_request_info():
        # Flush ensures we see logs in Railway immediately
        print(f">>> REQUEST: {request.method} {request.path}", flush=True)

    # ── Routes ────────────────────────────────────────────
    # ── Routes ────────────────────────────────────────────
    @app.route('/ping')
    def ping():
        return "pong", 200

    @app.route('/health')
    def health():
        db_status = "untested"
        try:
            from database.connection import query
            query("SELECT 1", fetch_one=True)
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "status": "ok",
            "database": db_status,
            "port": os.getenv("PORT", "unknown")
        }, 200

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the full traceback to Railway console
        import traceback
        print(f">>> ERROR: {str(e)}", flush=True)
        traceback.print_exc()
        return "Internal Server Error", 500

    # Direct Index Fallback (Emergency Route if Blueprint fails)
    @app.route('/index_direct')
    def index_direct():
        return render_template('public/index.html')

    # Register context processors
    from utils.storage import get_storage_url
    @app.context_processor
    def inject_storage():
        return dict(storage_url=get_storage_url)

    print(">>> Flask App Created and Configured. Registered Routes:", flush=True)
    for rule in app.url_map.iter_rules():
        print(f">>> ROUTE: {rule.endpoint} -> {rule}", flush=True)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=os.getenv('PORT', 5000))
