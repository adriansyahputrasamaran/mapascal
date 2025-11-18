import os # Ensure os is imported first for load_dotenv check
from dotenv import load_dotenv # Import load_dotenv
load_dotenv() # Load environment variables from .env for local development

from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
import logging
from logging.handlers import RotatingFileHandler
from app.decorators import requires_role, owns_resource # Import decorators
from flask_talisman import Talisman # Import Talisman

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://" # Use in-memory storage
)
talisman = Talisman() # Initialize Talisman

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Security check for SECRET_KEY
    secret_key = app.config.get('SECRET_KEY')
    if not secret_key:
        app.logger.critical('FATAL ERROR: SECRET_KEY is not set. Aborting startup.')
        raise ValueError('SECRET_KEY must be set in the environment or .env file.')
    if len(secret_key) < 32:
        app.logger.critical('FATAL ERROR: SECRET_KEY is too weak (less than 32 characters). Aborting startup.')
        raise ValueError('SECRET_KEY must be at least 32 characters long.')

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register user_loader and import models within app context
    from app.models import User, SuratMasuk, SuratKeluar
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Log email configuration for debugging
    app.logger.debug(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    app.logger.debug(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    app.logger.debug(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    app.logger.debug(f"MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
    app.logger.debug(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")

    # Initialize Talisman with CSP and HSTS
    talisman.init_app(app,
        content_security_policy={
            'default-src': ["'self'"],
            'script-src': ["'self'", 'https://cdn.jsdelivr.net'],
            'style-src': ["'self'", 'https://cdn.jsdelivr.net', 'https://cdnjs.cloudflare.com'],
            'img-src': ["'self'", 'data:'],
            'font-src': ["'self'", 'https://cdnjs.cloudflare.com'],
            'object-src': ["'none'"], # Prevent embedding of Flash, etc.
            'base-uri': ["'self'"], # Restrict base URL
            'form-action': ["'self'"], # Restrict form submissions
            'frame-ancestors': ["'none'"], # Prevent clickjacking
        },
        content_security_policy_nonce_in=['script-src'], # Add nonce to script tags
        force_https=not app.config['DEBUG'], # Set to True in production with HTTPS
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        strict_transport_security_include_subdomains=True,
        strict_transport_security_preload=True,
        frame_options='DENY',
        x_content_type_options=True,
        x_xss_protection=True
    )

    @app.after_request
    def remove_server_headers(response):
        # Remove Server and X-Powered-By headers for Server Version Disclosure
        response.headers.pop('Server', None)
        response.headers.pop('X-Powered-By', None)
        return response

    # Configure logging
    if not os.path.exists('app/logs'):
        os.mkdir('app/logs')
    file_handler = RotatingFileHandler('app/logs/security.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MAPASCAL startup')

    from app.routes.auth import auth_bp
    from app.routes.surat_masuk import surat_masuk_bp
    from app.routes.surat_keluar import surat_keluar_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(surat_masuk_bp)
    app.register_blueprint(surat_keluar_bp)

    from werkzeug.exceptions import RequestEntityTooLarge
    from flask import flash, redirect, request

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_size_error(e):
        flash('Ukuran file terlalu besar. Maksimal 16 MB.', 'danger')
        return redirect(request.url)

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f"Bad Request: {request.url} from {request.remote_addr}")
        return render_template('error_400.html'), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"Forbidden Access: {request.url} by user {current_user.get_id() if current_user.is_authenticated else 'anonymous'} from {request.remote_addr}")
        return render_template('error_403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"Not Found: {request.url} from {request.remote_addr}")
        return render_template('error_404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal Server Error: {error} at {request.url} from {request.remote_addr}", exc_info=True)
        return render_template('error_500.html'), 500

    # Example of setting specific CORS headers if needed for a specific origin
    # @app.after_request
    # def after_request_func(response):
    #     response.headers.add("Access-Control-Allow-Origin", "https://trusted-domain.com")
    #     response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    #     response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    #     return response

    return app


