from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, DateField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo, Email
from datetime import date
from app.models import User # Import User model for validation

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role_selection = SelectField('Login Sebagai', choices=[('anggota', 'Anggota'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=50)])
    nama_lengkap = StringField('Nama Lengkap', validators=[DataRequired(), Length(min=3, max=100)])
    nama_lapangan = StringField('Nama Lapangan (Opsional)', validators=[Length(max=100)])
    nia = StringField('NIM / Nomor Induk Anggota', validators=[DataRequired(), Length(min=4, max=50)])
    jenjang_keanggotaan = SelectField('Jenjang Keanggotaan', choices=[
        ('Anggota Muda', 'Anggota Muda'),
        ('Anggota Penuh', 'Anggota Penuh'),
        ('Anggota Kehormatan', 'Anggota Kehormatan')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Daftar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username ini sudah digunakan. Mohon gunakan yang lain.')

    def validate_nia(self, nia):
        user = User.query.filter_by(nia=nia.data).first()
        if user:
            raise ValidationError('NIM/NIA ini sudah terdaftar. Mohon gunakan yang lain.')

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

class TokenVerificationForm(FlaskForm):
    access_token = StringField('Kode Akses', validators=[DataRequired()])
    submit = SubmitField('Verifikasi')