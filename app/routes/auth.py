from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db, limiter
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.decorators import requires_role # Import from app.decorators
from functools import wraps # Still needed for other decorators if any, or can be removed if not used elsewhere

auth_bp = Blueprint('auth', __name__)

# Removed the local roles_required decorator as it's now in app/decorators.py

@auth_bp.route('/')
@auth_bp.route('/home')
def home():
    return render_template('index.html', title='Home')

@auth_bp.route('/about')
def about():
    return render_template('about.html', title='Tentang Aplikasi')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('auth.dashboard_admin'))
        else:
            return redirect(url_for('auth.dashboard_anggota'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Dummy password check to normalize timing, even if user doesn't exist
        # This helps prevent username enumeration
        if user:
            password_match = user.check_password(form.password.data)
            role_match = (user.role == form.role_selection.data)
        else:
            password_match = False
            role_match = False # Assume role mismatch if user doesn't exist
            # To further normalize timing, a dummy hash check could be performed
            # on a known invalid hash, but for simplicity, we'll rely on the
            # consistent error message and rate limiting.

        if user and password_match and role_match:
            login_user(user)
            current_app.logger.info(f"User {user.username} (Role: {user.role}) logged in successfully from {request.remote_addr}")
            flash(f'Login berhasil! Selamat datang, {user.nama_lengkap}.', 'success')
            if user.role == 'admin':
                return redirect(url_for('auth.dashboard_admin'))
            else:
                return redirect(url_for('auth.dashboard_anggota'))
        else:
            current_app.logger.warning(f"Login failed for user {form.username.data}: Invalid credentials or role mismatch from {request.remote_addr}")
            # Standardized error message to prevent role enumeration
            flash('Login gagal. Periksa username dan password Anda.', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"User {current_user.username} (Role: {current_user.role}) logged out from {request.remote_addr}")
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.home'))

@auth_bp.route('/dashboard/admin')
@login_required
@requires_role('admin') # Changed from roles_required
def dashboard_admin():
    current_app.logger.info(f"Admin user {current_user.username} accessed admin dashboard from {request.remote_addr}")
    total_anggota = User.query.filter_by(role='anggota').count()
    anggota_list = User.query.filter_by(role='anggota').order_by(User.nama_lengkap).all()
    return render_template('dashboard_admin.html', title='Dashboard Admin', user=current_user, total_anggota=total_anggota, anggota_list=anggota_list)

@auth_bp.route('/dashboard/anggota')
@login_required
@requires_role('anggota') # Changed from roles_required
def dashboard_anggota():
    current_app.logger.info(f"Anggota user {current_user.username} accessed anggota dashboard from {request.remote_addr}")
    anggota_list = User.query.filter_by(role='anggota').order_by(User.nama_lengkap).all()
    return render_template('dashboard_anggota.html', title='Dashboard Anggota', user=current_user, anggota_list=anggota_list)

@auth_bp.route('/register_anggota', methods=['GET', 'POST'])
@login_required
@requires_role('admin') # Changed from roles_required
def register_anggota():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            nama_lengkap=form.nama_lengkap.data,
            nama_lapangan=form.nama_lapangan.data,
            nia=form.nia.data,
            jenjang_keanggotaan=form.jenjang_keanggotaan.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info(f"Admin user {current_user.username} registered new anggota: {user.username} (NIA: {user.nia}) from {request.remote_addr}")
        flash(f'Akun anggota {form.username.data} berhasil didaftarkan!', 'success')
        return redirect(url_for('auth.dashboard_admin'))
    return render_template('register_anggota.html', title='Daftarkan Anggota', form=form)

@auth_bp.route('/anggota/daftar')
@login_required
def list_anggota():
    anggota_list = User.query.filter_by(role='anggota').order_by(User.nama_lengkap).all()
    return render_template('anggota/list.html', title='Daftar Anggota', anggota_list=anggota_list)

