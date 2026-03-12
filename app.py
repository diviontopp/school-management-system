print(">>> BOOT: app.py is starting imports...", flush=True)
import os
import sys
from flask import Flask, render_template, request, send_from_directory
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
    print(f">>> DEBUG: Static Folder: {app.static_folder}", flush=True)
    print(f">>> DEBUG: Static URL Path: {app.static_url_path}", flush=True)
    
    # WhiteNoise for static files (CRITICAL for Gunicorn!)
    # Should wrap the app before ProxyFix to ensure it handles static files first
    # Using autorefresh=True for debugging purposes
    app.wsgi_app = WhiteNoise(app.wsgi_app, 
                             root=app.static_folder, 
                             prefix=app.static_url_path + '/',
                             autorefresh=True)
    
    # Trust Railway Edge Proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    # ── Logging ───────────────────────────────────────────
    @app.before_request
    def log_request_info():
        print(f">>> REQUEST: {request.method} {request.path}", flush=True)

    # ── Fail-safe Core Routes ─────────────────────────────
    # The '/' route is already handled by public_bp.index
    # We keep a health check but remove the redundant root route to avoid conflicts

    @app.route('/health')
    def health():
        return {"status": "ok", "env": "production"}, 200

    @app.route('/debug-static')
    def debug_static():
        target = 'images/dbx_gallery/gallery_img_15.jpg'
        full_path = os.path.join(app.static_folder, target)
        exists = os.path.exists(full_path)
        contents = os.listdir(app.static_folder) if os.path.exists(app.static_folder) else "DIR_NOT_FOUND"
        return {
            "target": target,
            "static_folder": app.static_folder,
            "full_path": full_path,
            "exists": exists,
            "static_contents": contents[:10], # First 10 items
            "cwd": os.getcwd()
        }

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static/images'),
                                   'icon.jpg', mimetype='image/vnd.microsoft.icon')

    from werkzeug.exceptions import HTTPException
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Pass through HTTP errors like 404, log only real crashes"""
        if isinstance(e, HTTPException):
            return e
            
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
