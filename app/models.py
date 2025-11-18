from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # Tetap sebagai username, tapi tidak untuk login anggota
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    nama_lapangan = db.Column(db.String(100), nullable=True)
    nia = db.Column(db.String(50), unique=True, nullable=False) # Digunakan untuk login anggota
    jenjang_keanggotaan = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='anggota') # 'admin' or 'anggota'
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    access_token_hash = db.Column(db.String(255), nullable=True) # Store hashed access token
    access_token_expiration = db.Column(db.DateTime, nullable=True) # Token expiration time
    access_token_used = db.Column(db.Boolean, default=False, nullable=False) # For one-time use
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    surat_masuk_uploaded = db.relationship('SuratMasuk', backref='uploader', lazy=True)
    surat_keluar_uploaded = db.relationship('SuratKeluar', backref='uploader', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_access_token(self, token, expires_in_seconds=300): # Default 5 minutes
        self.access_token_hash = generate_password_hash(token)
        self.access_token_expiration = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        self.access_token_used = False

    def check_access_token(self, token):
        if not self.access_token_hash:
            return False
        return check_password_hash(self.access_token_hash, token)

    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

class SuratMasuk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomor_surat = db.Column(db.String(100), unique=True, nullable=False)
    asal_surat = db.Column(db.String(100), nullable=False)
    tanggal_terima = db.Column(db.Date, nullable=False)
    perihal = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SuratMasuk {self.nomor_surat}>'

class SuratKeluar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nomor_surat = db.Column(db.String(100), unique=True, nullable=False)
    tujuan_surat = db.Column(db.String(100), nullable=False)
    tanggal_surat = db.Column(db.Date, nullable=False)
    perihal = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SuratKeluar {self.nomor_surat}>'

