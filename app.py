print(">>> BOOT: app.py is starting imports...", flush=True)
import os
import sys
from flask import Flask, render_template, request
from config import Config
print(f">>> BOOT: Config loaded. MYSQL_HOST={'set' if Config.MYSQL_HOST else 'None'}...", flush=True)
from flask_talisman import Talisman
from database.connection import initialize_database

from werkzeug.middleware.proxy_fix import ProxyFix
from whitenoise import WhiteNoise

def create_app():
    print(">>> Creating Flask App...", flush=True)
    
    # Absolute paths to avoid resolution issues in production
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'),
                static_url_path='/static')
    
    app.config.from_object(Config)

    # ── Blueprint Registration (Top Priority) ──────────────
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

    # ── Middleware ──────────────────────────────────────────
    # Trust Railway Edge Proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    # WhiteNoise for static files (CRITICAL for Gunicorn!)
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(base_dir, 'static/'), prefix='/static/')

    # ── Logging ───────────────────────────────────────────
    @app.before_request
    def log_request_info():
        print(f">>> REQUEST: {request.method} {request.path}", flush=True)

    # ── Fail-safe Core Routes ─────────────────────────────
    @app.route('/')
    def root_landing_page():
        """Bypasses blueprint to ensure landing page always works"""
        return render_template('public/index.html')

    @app.route('/health')
    def health():
        return {"status": "ok", "env": "production"}, 200

    @app.errorhandler(Exception)
    def handle_exception(e):
        import traceback
        print(f">>> ERROR: {str(e)}", flush=True)
        traceback.print_exc()
        return "Internal Server Error", 500

    # Register context processors
    from utils.storage import get_storage_url
    @app.context_processor
    def inject_storage():
        return dict(storage_url=get_storage_url)

    print(">>> Flask App Created and Fully Hardened.", flush=True)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=os.getenv('PORT', 5000))
