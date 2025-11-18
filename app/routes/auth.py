

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
import secrets
from datetime import datetime # Added for token expiration check
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from app import db, limiter
from app.models import User
from app.forms import LoginForm, RegistrationForm, TokenVerificationForm
from app.decorators import requires_role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/home')
def home():
    return render_template('index.html', title='Home')

@auth_bp.route('/about')
def about():
    return render_template('about.html', title='Tentang Aplikasi')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('auth.dashboard_admin'))
        else:
            return redirect(url_for('auth.dashboard_anggota'))

    form = LoginForm()
    if form.validate_on_submit():
        role = form.role_selection.data
        identifier = form.username.data # This field holds username for admin, NIA for anggota
        
        if role == 'admin':
            user = User.query.filter(
                User.role == 'admin',
                or_(User.username == identifier, User.nia == identifier)
            ).first()
            if user and user.check_password(form.password.data):
                # Reset failed login attempts on successful login
                session.pop('failed_login_attempts', None)
                if not user.is_active:
                    user.is_active = True
                    db.session.commit()
                login_user(user)
                current_app.logger.info(f"Admin user {user.username} logged in successfully from {request.remote_addr}")
                flash(f'Login berhasil! Selamat datang, {user.nama_lengkap}.', 'success')
                return redirect(url_for('auth.dashboard_admin'))
            else:
                # Log failed attempt
                failed_attempts = session.get('failed_login_attempts', {})
                key = f"{role}:{identifier}" # Use a string key instead of a tuple
                failed_attempts[key] = failed_attempts.get(key, 0) + 1
                session['failed_login_attempts'] = failed_attempts

                if failed_attempts[key] >= 3: # Log warning after 3 failed attempts
                    current_app.logger.warning(f"Brute-force attempt detected for admin {identifier} from {request.remote_addr}. Failed attempts: {failed_attempts[key]}")
                else:
                    current_app.logger.warning(f"Login failed for admin {identifier} from {request.remote_addr}")
                flash('Login gagal. Periksa username dan password Anda.', 'danger')
        
        elif role == 'anggota':
            user = User.query.filter_by(username=identifier, role='anggota').first()
            
            if not (user and user.check_password(form.password.data)):
                # Log failed attempt
                failed_attempts = session.get('failed_login_attempts', {})
                key = f"{role}:{identifier}" # Use a string key instead of a tuple
                failed_attempts[key] = failed_attempts.get(key, 0) + 1
                session['failed_login_attempts'] = failed_attempts

                if failed_attempts[key] >= 3: # Log warning after 3 failed attempts
                    current_app.logger.warning(f"Brute-force attempt detected for NIA {identifier} from {request.remote_addr}. Failed attempts: {failed_attempts[key]}")
                else:
                    current_app.logger.warning(f"Login failed for NIA {identifier}: Invalid credentials from {request.remote_addr}")
                flash('Kredensial tidak valid.', 'danger')
                return render_template('login.html', title='Login', form=form)

            # Reset failed login attempts on successful login
            session.pop('failed_login_attempts', None)

            if not user.is_active:
                current_app.logger.warning(f"Login failed for NIA {identifier}: Account not active from {request.remote_addr}")
                flash('Akun Anda belum diverifikasi admin.', 'warning')
                return render_template('login.html', title='Login', form=form)

            # Store user ID in session for 2FA verification
            session['two_factor_user_id'] = user.id
            return redirect(url_for('auth.verify_token'))

    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/verify-token', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def verify_token():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('auth.dashboard_admin'))
        else:
            return redirect(url_for('auth.dashboard_anggota'))

    if 'two_factor_user_id' not in session:
        flash('Silakan login terlebih dahulu.', 'info')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['two_factor_user_id'])
    if not user:
        flash('Pengguna tidak ditemukan.', 'danger')
        return redirect(url_for('auth.login'))

    form = TokenVerificationForm()
    if form.validate_on_submit():
        # Check if token exists and is not used
        if not user.access_token_hash or user.access_token_used:
            current_app.logger.warning(f"2FA failed for user {user.username} (NIA: {user.nia}): Token not set or already used from {request.remote_addr}")
            flash('Kode akses tidak valid atau sudah digunakan.', 'danger')
            return render_template('verify_token.html', title='Verifikasi Kode Akses', form=form)

        # Check for token expiration
        if user.access_token_expiration and datetime.utcnow() > user.access_token_expiration:
            current_app.logger.warning(f"2FA failed for user {user.username} (NIA: {user.nia}): Expired access token from {request.remote_addr}")
            flash('Kode akses telah kedaluwarsa. Silakan minta kode baru.', 'danger')
            # Optionally, invalidate the token here if it's expired but not yet marked used
            user.access_token_hash = None
            user.access_token_expiration = None
            db.session.commit()
            return render_template('verify_token.html', title='Verifikasi Kode Akses', form=form)

        # Verify the token
        if user.check_access_token(form.access_token.data):
            user.access_token_used = True # Mark token as used
            db.session.commit()
            login_user(user)
            del session['two_factor_user_id'] # Clear temporary session data
            current_app.logger.info(f"Anggota user {user.username} (NIA: {user.nia}) logged in successfully via 2FA from {request.remote_addr}")
            flash(f'Login berhasil! Selamat datang, {user.nama_lengkap}.', 'success')
            return redirect(url_for('auth.dashboard_anggota'))
        else:
            current_app.logger.warning(f"2FA failed for user {user.username} (NIA: {user.nia}): Invalid access token attempt from {request.remote_addr}")
            flash('Kode akses salah. Mohon coba lagi.', 'danger')
    
    return render_template('verify_token.html', title='Verifikasi Kode Akses', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    current_app.logger.info(f"User {current_user.username} (Role: {current_user.role}) logged out from {request.remote_addr}")
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.home'))

@auth_bp.route('/dashboard/admin')
@login_required
@requires_role('admin')
def dashboard_admin():
    current_app.logger.info(f"Admin user {current_user.username} accessed admin dashboard from {request.remote_addr}")
    
    # The list of members is now managed on a separate page
    total_anggota = User.query.filter_by(role='anggota').count()
    
    return render_template('dashboard_admin.html', title='Dashboard Admin', user=current_user, total_anggota=total_anggota)

@auth_bp.route('/admin/members')
@login_required
@requires_role('admin')
def manage_members():
    current_app.logger.info(f"Admin user {current_user.username} accessed member management page from {request.remote_addr}")
    anggota_list = User.query.filter_by(role='anggota').order_by(User.nama_lengkap).all()
    return render_template('admin/manage_members.html', title='Manajemen Anggota', anggota_list=anggota_list)

@auth_bp.route('/dashboard/anggota')
@login_required
@requires_role('anggota')
def dashboard_anggota():
    current_app.logger.info(f"Anggota user {current_user.username} accessed anggota dashboard from {request.remote_addr}")
    anggota_list = User.query.filter_by(role='anggota').order_by(User.nama_lengkap).all()
    return render_template('dashboard_anggota.html', title='Dashboard Anggota', user=current_user, anggota_list=anggota_list)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            nama_lengkap=form.nama_lengkap.data,
            nama_lapangan=form.nama_lapangan.data,
            nia=form.nia.data,
            jenjang_keanggotaan=form.jenjang_keanggotaan.data,
            role='anggota',
            is_active=False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        current_app.logger.info(f"New user pending approval: {user.username} from {request.remote_addr}.")
        flash('Pendaftaran berhasil! Akun Anda sedang menunggu persetujuan dari Admin.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Daftar Akun', form=form)

@auth_bp.route('/anggota/daftar')
@login_required
def list_anggota():
    anggota_list = User.query.filter_by(role='anggota').order_by(User.nama_lengkap).all()
    return render_template('anggota/list.html', title='Daftar Anggota', anggota_list=anggota_list)

@auth_bp.route('/admin/pendaftaran')
@login_required
@requires_role('admin')
def pending_registrations():
    pending_users = User.query.filter_by(is_active=False, role='anggota').order_by(User.created_at.desc()).all()
    current_app.logger.debug(f"DEBUG: Pending users found: {[user.username for user in pending_users]}")
    return render_template('admin/pendaftaran_list.html', title='Pendaftaran Pending', users=pending_users)

@auth_bp.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
@requires_role('admin')
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_active:
        flash(f'Anggota "{user.nama_lengkap}" sudah aktif.', 'info')
        return redirect(url_for('auth.pending_registrations'))

    access_token = secrets.token_hex(6)

    user.is_active = True
    user.set_access_token(access_token) # Hash token, set expiration, mark as unused
    db.session.commit()

    current_app.logger.info(f"Admin {current_user.username} approved user {user.username} (NIA: {user.nia}).")
    flash(f'Anggota "{user.nama_lengkap}" telah berhasil diaktifkan. Berikan Kode Akses berikut kepadanya: {access_token}', 'success')
    
    return redirect(url_for('auth.manage_members'))

@auth_bp.route('/admin/reissue-token/<int:user_id>', methods=['POST'])
@login_required
@requires_role('admin')
def reissue_token(user_id):
    user = User.query.get_or_404(user_id)
    
    # For simplicity, we allow reissuing for any active member.
    # A more complex check could verify if the user has ever logged in.
    
    access_token = secrets.token_hex(6)
    user.set_access_token(access_token) # This method resets expiration and used status
    db.session.commit()

    current_app.logger.info(f"Admin {current_user.username} reissued access token for user {user.username} (NIA: {user.nia}).")
    flash(f'Kode akses baru untuk "{user.nama_lengkap}" adalah: {access_token}', 'success')
    
    return redirect(url_for('auth.manage_members'))
