from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # Tetap sebagai username login
    password_hash = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    nama_lapangan = db.Column(db.String(100), nullable=True)
    nia = db.Column(db.String(50), unique=True, nullable=False) # Field baru untuk NIA
    jenjang_keanggotaan = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), nullable=False) # 'admin' or 'anggota'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    surat_masuk_uploaded = db.relationship('SuratMasuk', backref='uploader', lazy=True)
    surat_keluar_uploaded = db.relationship('SuratKeluar', backref='uploader', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
