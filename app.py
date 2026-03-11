import os
import sys
from flask import Flask, render_template
from config import Config
from flask_talisman import Talisman
from database.connection import initialize_database

from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    # ── Database Initialization ────────────────────────────────
    # Run in a background thread so it does NOT block gunicorn startup.
    # Railway's health check will pass immediately; init happens concurrently.
    if os.getenv("INIT_DB", "False") == "True":
        import threading
        init_thread = threading.Thread(target=initialize_database, daemon=True)
        init_thread.start()

    base_dir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'),
                static_url_path='/static')
    
    # Apply ProxyFix for Railway/HuggingFace reverse proxies
    # x_for=1, x_host=1, x_proto=1, x_port=1, x_prefix=1
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    
    # Enable WhiteNoise for robust static file serving on Railway
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(base_dir, 'static/'), prefix='/static/')

    app.config.from_object(Config)

    # Initialize Security Headers
    # We allow inline scripts/styles for this specific educational layout where CSS variables and simple logics are injected linearly.
    csp = {
        'default-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "cdnjs.cloudflare.com", "unpkg.com", "fonts.googleapis.com", "fonts.gstatic.com", "cdn.jsdelivr.net", "ka-f.fontawesome.com"],
        'img-src': ["'self'", "data:", "https:"]
    }
    Talisman(app, 
             content_security_policy=csp, 
             content_security_policy_nonce_in=['script-src', 'style-src'],
             force_https=False,
             session_cookie_secure=True,
             session_cookie_http_only=True,
             session_cookie_samesite='Lax'
    )

    # Ensure upload folder exists (ignore errors on read-only file systems like Vercel)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except OSError:
        pass

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

    # ── Health Check ──────────────────────────────────────
    @app.route('/health')
    def health_check():
        """Lightweight health check for Railway."""
        from database.connection import query
        try:
            # Simple query to check DB connectivity
            query("SELECT 1")
            return {"status": "healthy", "database": "connected"}, 200
        except Exception as e:
            return {"status": "degraded", "database": str(e)}, 200 # Still return 200 so Railway doesn't kill the app during init

    # ── Error Handlers ────────────────────────────────────
    # Handle 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/favicon.ico')
    def favicon():
        return "", 204

    # Register context processors
    from utils.storage import get_storage_url
    @app.context_processor
    def inject_storage():
        return dict(storage_url=get_storage_url)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=os.getenv('PORT', 5000))
