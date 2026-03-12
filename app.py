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
    print(">>> Creating Flask App...", flush=True)
    
    # Absolute paths to avoid resolution issues in production
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'),
                static_url_path='/static')
    
    app.config.from_object(Config)

    # ── Blueprint Registration (Top Priority) ──────────────
    print(">>> BOOT: Registering Blueprints...", flush=True)
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
    print(">>> BOOT: Blueprints Registered.", flush=True)

    # ── Middleware ──────────────────────────────────────────
    print(f">>> DEBUG: Static Folder: {app.static_folder}", flush=True)
    print(f">>> DEBUG: Static URL Path: {app.static_url_path}", flush=True)
    
    # WhiteNoise for static files (CRITICAL for Gunicorn!)
    print(">>> BOOT: Initializing WhiteNoise...", flush=True)
    # Use the absolute static folder path explicitly
    static_dir = os.path.abspath(app.static_folder)
    app.wsgi_app = WhiteNoise(app.wsgi_app, 
                             root=static_dir, 
                             prefix='/static/',
                             index_file=True)
    
    # Trust Railway Edge Proxy
    print(">>> BOOT: Initializing ProxyFix...", flush=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    print(">>> BOOT: Middleware Initialized.", flush=True)

    # ── Logging ───────────────────────────────────────────
    @app.before_request
    def log_request_info():
        print(f">>> REQUEST: {request.method} {request.path}", flush=True)

    # ── Fail-safe Core Routes ─────────────────────────────
    @app.route('/health')
    def health():
        return {"status": "ok", "env": "production"}, 200

    @app.route('/debug-static')
    def debug_static():
        target = 'images/dbx_gallery/gallery_img_15.jpg'
        full_path = os.path.join(app.static_folder, target)
        exists = os.path.exists(full_path)
        size = os.path.getsize(full_path) if exists else -1
        
        # Test if we can actually read the file content
        content_peek = "N/A"
        try:
            if exists:
                with open(full_path, 'rb') as f:
                    content_peek = f.read(10).hex()
        except Exception as e:
            content_peek = f"ERROR_READING: {str(e)}"

        contents = os.listdir(app.static_folder) if os.path.exists(app.static_folder) else "DIR_NOT_FOUND"
        return {
            "target": target,
            "static_folder": app.static_folder,
            "full_path": full_path,
            "exists": exists,
            "size": size,
            "read_test": content_peek,
            "static_contents": contents[:10],
            "cwd": os.getcwd()
        }

    @app.route('/test-static-direct')
    def test_static_direct():
        return send_from_directory(os.path.join(app.root_path, 'static/images/dbx_gallery'),
                                   'gallery_img_15.jpg')

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
