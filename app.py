import os
import sys
from flask import Flask, render_template, request
from config import Config
from flask_talisman import Talisman
from database.connection import initialize_database

from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    print(">>> Creating Flask App...", flush=True)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'),
                static_url_path='/static')
    
    # ── Middleware ──────────────────────────────────────────
    # Simple ProxyFix for Railway
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    
    # WhiteNoise for static files
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(base_dir, 'static/'), prefix='/static/')

    app.config.from_object(Config)

    # Talisman with relaxed settings for debugging
    csp = {
        'default-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "*"],
        'img-src': ["'self'", "data:", "https:", "*"]
    }
    Talisman(app, 
             content_security_policy=csp, 
             force_https=False,
             session_cookie_secure=False # Set to True in prod if HTTPS is guaranteed
    )

    # ── Logging ───────────────────────────────────────────
    @app.before_request
    def log_request_info():
        print(f">>> REQUEST: {request.method} {request.path}", flush=True)

    # ── Routes ────────────────────────────────────────────
    @app.route('/ping')
    def ping():
        return "pong", 200

    @app.route('/health')
    def health():
        return {"status": "ok"}, 200

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
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

    # Register context processors
    from utils.storage import get_storage_url
    @app.context_processor
    def inject_storage():
        return dict(storage_url=get_storage_url)

    print(">>> Flask App Created and Configured.", flush=True)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=os.getenv('PORT', 5000))
