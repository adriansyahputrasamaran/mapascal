import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Ambil DATABASE_URL dari Railway
    db_url = os.environ.get("DATABASE_URL")

    if db_url:
        # Pastikan kompatibel dengan SQLAlchemy + PyMySQL
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)

        # Jika port tidak ada, tambahkan :3306 secara otomatis
        if '@' in db_url and ':' not in db_url.split('@')[1].split('/')[0]:
            # Format sebelum:  user:pass@host/database
            # Format sesudah: user:pass@host:3306/database
            parts = db_url.split('@')
            left = parts[0]   # user:pass
            right = parts[1]  # host/database
            host, dbname = right.split('/', 1)
            right = f"{host}:3306/{dbname}"
            db_url = left + '@' + right

        SQLALCHEMY_DATABASE_URI = db_url

    else:
        # Fallback ke variabel ENV lainnya (jaga-jaga)
        db_port = os.environ.get("MYSQLPORT", "3306")
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.environ.get('MYSQLUSER')}:"
            f"{os.environ.get('MYSQLPASSWORD')}@"
            f"{os.environ.get('MYSQLHOST')}:{db_port}/"
            f"{os.environ.get('MYSQLDATABASE')}"
        )

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
