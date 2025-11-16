import os
# from dotenv import load_dotenv # Removed for production readiness

# load_dotenv() # Muat variabel dari .env - Removed for production readiness

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MYSQL_HOST = os.environ.get("MYSQLHOST")
    MYSQL_PORT = os.environ.get("MYSQLPORT")
    MYSQL_USER = os.environ.get("MYSQLUSER")
    MYSQL_PASSWORD = os.environ.get("MYSQLPASSWORD")
    MYSQL_DB = os.environ.get("MYSQLDATABASE")

    SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://root:hNORIFRysdBfIehFKGjrQFWNrBWHdqAg@shuttle.proxy.rlwy.net:42948/railway"
)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('FLASK_DEBUG') == 'True' # Set DEBUG based on FLASK_DEBUG env var
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/uploads') # Configurable upload folder

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # Cek koneksi sebelum query
        "pool_recycle": 280,     # Reset pool sebelum MySQL timeouts
        "pool_size": 3,          # Pool kecil -> cocok untuk Railway
        "max_overflow": 0        # Jangan buat koneksi tambahan
    }

    # Admin Contact Information
    ADMIN_CONTACT_PHONE = '0822-9325-2854'
    ADMIN_CONTACT_EMAIL = 'adriansyahputrasamaran@gmail.com'
    ADMIN_CONTACT_NAME = 'Adrian Pecinta Alam'

    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Megabytes

    # Session Security
    SESSION_COOKIE_SECURE = True  # Hanya kirim cookie melalui HTTPS
    SESSION_COOKIE_HTTPONLY = True # Mencegah akses cookie via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax' # Melindungi dari CSRF (modern browsers)
    REMEMBER_COOKIE_SECURE = True # Jika menggunakan Flask-Login remember me
    REMEMBER_COOKIE_HTTPONLY = True # Jika menggunakan Flask-Login remember me
    PERMANENT_SESSION_LIFETIME = 86400 # Sesi berlaku 1 hari (dalam detik)

    # CSRF Protection
    WTF_CSRF_ENABLED = True
