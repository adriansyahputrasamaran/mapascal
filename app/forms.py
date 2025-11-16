from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, DateField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from datetime import date
from app.models import User # Import User model for validation

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role_selection = SelectField('Login Sebagai', choices=[('admin', 'Admin'), ('anggota', 'Anggota')], validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)]) # Kembali ke Username
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=100)])
    nama_lapangan = StringField('Nama Lapangan', validators=[DataRequired(), Length(min=3, max=100)])
    nia = StringField('Nomor Induk Anggota (NIA)', validators=[DataRequired(), Length(min=4, max=50)]) # Field baru
    jenjang_keanggotaan = SelectField('Jenjang Keanggotaan', choices=[
        ('Anggota Muda', 'Anggota Muda'),
        ('Anggota Penuh', 'Anggota Penuh'),
        ('Anggota Kehormatan', 'Anggota Kehormatan')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Peran', choices=[('anggota', 'Anggota')], validators=[DataRequired()])
    submit = SubmitField('Daftarkan Anggota')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username ini sudah terdaftar. Mohon gunakan username lain.')

    def validate_nia(self, nia): # Validasi baru untuk NIA
        user = User.query.filter_by(nia=nia.data).first()
        if user:
            raise ValidationError('NIA ini sudah terdaftar. Mohon gunakan NIA lain.')

class SuratMasukForm(FlaskForm):
    nomor_surat = StringField('Nomor Surat', validators=[DataRequired(), Length(max=100)])
    asal_surat = StringField('Asal Surat', validators=[DataRequired(), Length(max=100)])
    tanggal_terima = DateField('Tanggal Terima', format='%Y-%m-%d', validators=[DataRequired()])
    perihal = TextAreaField('Perihal', validators=[DataRequired()])
    file_surat = FileField('File Surat (PDF, DOCX, JPG, max 5MB)', validators=[
        FileAllowed(['pdf', 'docx', 'jpg', 'jpeg'], 'Hanya file PDF, DOCX, dan JPG/JPEG yang diizinkan!'),
    ])
    submit = SubmitField('Simpan')

    def validate_file_surat(self, field):
        if field.data:
            if field.data.content_length > 5 * 1024 * 1024: # 5 MB
                raise ValidationError('Ukuran file terlalu besar (maksimal 5MB).')

class SuratKeluarForm(FlaskForm):
    nomor_surat = StringField('Nomor Surat', validators=[DataRequired(), Length(max=100)])
    tujuan_surat = StringField('Tujuan Surat', validators=[DataRequired(), Length(max=100)])
    tanggal_surat = DateField('Tanggal Surat', format='%Y-%m-%d', validators=[DataRequired()])
    perihal = TextAreaField('Perihal', validators=[DataRequired()])
    file_surat = FileField('File Surat (PDF, DOCX, JPG, max 5MB)', validators=[
        FileAllowed(['pdf', 'docx', 'jpg', 'jpeg'], 'Hanya file PDF, DOCX, dan JPG/JPEG yang diizinkan!'),
    ])
    submit = SubmitField('Simpan')

    def validate_file_surat(self, field):
        if field.data:
            if field.data.content_length > 5 * 1024 * 1024: # 5 MB
                raise ValidationError('Ukuran file terlalu besar (maksimal 5MB).')
