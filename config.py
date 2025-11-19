import os
import urllib.parse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Set database URI. Prioritize DATABASE_URL from Railway.
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Parse the database URL
        parsed_url = urllib.parse.urlparse(db_url)
        
        # Build the new URL with the correct scheme for SQLAlchemy (mysql+pymysql)
        # This is more robust than a simple string replacement.
        SQLALCHEMY_DATABASE_URI = urllib.parse.urlunparse(
            (
                'mysql+pymysql',
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            )
        )
    else:
        # Fallback for local or other environments using individual variables.
        # Provide a default port to prevent errors.
        user = os.environ.get('MYSQLUSER')
        password = os.environ.get('MYSQLPASSWORD')
        host = os.environ.get('MYSQLHOST')
        port = os.environ.get('MYSQLPORT', '3306')
        db_name = os.environ.get('MYSQLDATABASE')
        
        # Only construct the URI if all essential parts are present
        if all([user, password, host, db_name]):
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
        else:
            # If essential parts are missing, set URI to None to cause a clear failure.
            # This is better than a malformed URI.
            SQLALCHEMY_DATABASE_URI = None

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_DEBUG') == 'True'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/uploads')

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 3,
        "max_overflow": 0
    }

    ADMIN_CONTACT_PHONE = '0822-9325-2854'
    ADMIN_CONTACT_EMAIL = 'adriansyahputrasamaran@gmail.com'
    ADMIN_CONTACT_NAME = 'Adrian Pecinta Alam'

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400

    WTF_CSRF_ENABLED = True
