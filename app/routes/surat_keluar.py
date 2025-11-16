from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models import SuratKeluar, User
from app.forms import SuratKeluarForm
from app.decorators import requires_role, owns_resource # Updated import
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import filetype

surat_keluar_bp = Blueprint('surat_keluar', __name__, url_prefix='/surat_keluar')

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'uploads', 'surat_keluar')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'image/jpeg'
}

def is_allowed_file(file_stream):
    try:
        # Read the first 2048 bytes to determine the mime type
        mime_type = magic.from_buffer(file_stream.read(2048), mime=True)
        file_stream.seek(0)  # Reset stream position
        return mime_type in ALLOWED_MIME_TYPES
    except Exception:
        return False

@surat_keluar_bp.route('/')
@login_required
def list_surat_keluar():
    # Whitelist for query parameters
    allowed_search_by = ['nomor_surat', 'tujuan_surat', 'perihal']
    allowed_sort_by = ['nomor_surat', 'tujuan_surat', 'tanggal_surat', 'perihal']
    allowed_sort_order = ['asc', 'desc']

    # Get and validate parameters
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '', type=str)
    search_by = request.args.get('search_by', 'nomor_surat', type=str)
    start_date_str = request.args.get('start_date', '', type=str)
    end_date_str = request.args.get('end_date', '', type=str)
    sort_by = request.args.get('sort_by', 'tanggal_surat', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)

    # Validate against whitelists
    if search_by not in allowed_search_by:
        search_by = 'nomor_surat'
    if sort_by not in allowed_sort_by:
        sort_by = 'tanggal_surat'
    if sort_order not in allowed_sort_order:
        sort_order = 'desc'

    query = SuratKeluar.query

    # Filter based on user role
    if current_user.role == 'anggota':
        query = query.filter_by(uploaded_by_user_id=current_user.id)

    # Apply search filters
    if search_query:
        if search_by == 'nomor_surat':
            query = query.filter(SuratKeluar.nomor_surat.ilike(f'%{search_query}%'))
        elif search_by == 'tujuan_surat':
            query = query.filter(SuratKeluar.tujuan_surat.ilike(f'%{search_query}%'))
        elif search_by == 'perihal':
            query = query.filter(SuratKeluar.perihal.ilike(f'%{search_query}%'))

    # Apply date filters
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(SuratKeluar.tanggal_surat >= start_date)
        except ValueError:
            flash('Format tanggal mulai tidak valid.', 'warning')
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(SuratKeluar.tanggal_surat <= end_date)
        except ValueError:
            flash('Format tanggal akhir tidak valid.', 'warning')

    # Apply sorting
    sort_column = getattr(SuratKeluar, sort_by, SuratKeluar.tanggal_surat)
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    surat_keluar_list = query.paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'surat_keluar/list.html',
        title='Surat Keluar',
        surat_keluar_list=surat_keluar_list,
        search_query=search_query,
        search_by=search_by,
        start_date=start_date_str,
        end_date=end_date_str,
        sort_by=sort_by,
        sort_order=sort_order
    )
@surat_keluar_bp.route('/add', methods=['GET', 'POST'])
@login_required
@requires_role('admin') # Changed from roles_required
def add_surat_keluar():
    form = SuratKeluarForm()
    if form.validate_on_submit():
        if form.file_surat.data:
            file = form.file_surat.data
            
            if not is_allowed_file(file.stream):
                flash('Jenis file tidak diizinkan. Hanya PDF, DOCX, dan JPG yang diperbolehkan.', 'danger')
                return render_template('surat_keluar/form.html', title='Tambah Surat Keluar', form=form)

            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)

            surat_keluar = SuratKeluar(
                nomor_surat=form.nomor_surat.data,
                tujuan_surat=form.tujuan_surat.data,
                tanggal_surat=form.tanggal_surat.data,
                perihal=form.perihal.data,
                file_path=unique_filename,
                uploaded_by_user_id=current_user.id
            )
            db.session.add(surat_keluar)
            db.session.commit()
            current_app.logger.info(f"Admin user {current_user.username} added Surat Keluar: {surat_keluar.nomor_surat} from {request.remote_addr}")
            flash('Surat Keluar berhasil ditambahkan!', 'success')
            return redirect(url_for('surat_keluar.list_surat_keluar'))
        else:
            flash('File surat harus diunggah.', 'danger')
    return render_template('surat_keluar/form.html', title='Tambah Surat Keluar', form=form)

@surat_keluar_bp.route('/edit/<int:surat_id>', methods=['GET', 'POST'])
@login_required
@requires_role('admin') # Changed from roles_required
@owns_resource(SuratKeluar, 'surat_id') # Added owns_resource
def edit_surat_keluar(surat_id):
    surat_keluar = SuratKeluar.query.get_or_404(surat_id)
    form = SuratKeluarForm(obj=surat_keluar)
    if form.validate_on_submit():
        old_file_path = surat_keluar.file_path
        if form.file_surat.data:
            file = form.file_surat.data

            if not is_allowed_file(file.stream):
                flash('Jenis file tidak diizinkan. Hanya PDF, DOCX, dan JPG yang diperbolehkan.', 'danger')
                return render_template('surat_keluar/form.html', title='Edit Surat Keluar', form=form, surat_keluar=surat_keluar)

            # Delete old file
            if old_file_path and os.path.exists(os.path.join(UPLOAD_FOLDER, old_file_path)):
                os.remove(os.path.join(UPLOAD_FOLDER, old_file_path))

            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            surat_keluar.file_path = unique_filename

        surat_keluar.nomor_surat = form.nomor_surat.data
        surat_keluar.tujuan_surat = form.tujuan_surat.data
        surat_keluar.tanggal_surat = form.tanggal_surat.data
        surat_keluar.perihal = form.perihal.data
        surat_keluar.updated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"Admin user {current_user.username} edited Surat Keluar: {surat_keluar.nomor_surat} (ID: {surat_id}) from {request.remote_addr}")
        flash('Surat Keluar berhasil diperbarui!', 'success')
        return redirect(url_for('surat_keluar.list_surat_keluar'))
    return render_template('surat_keluar/form.html', title='Edit Surat Keluar', form=form, surat_keluar=surat_keluar)

@surat_keluar_bp.route('/delete/<int:surat_id>', methods=['POST'])
@login_required
@requires_role('admin') # Changed from roles_required
@owns_resource(SuratKeluar, 'surat_id') # Added owns_resource
def delete_surat_keluar(surat_id):
    surat_keluar = SuratKeluar.query.get_or_404(surat_id)
    if surat_keluar.file_path and os.path.exists(os.path.join(UPLOAD_FOLDER, surat_keluar.file_path)):
        os.remove(os.path.join(UPLOAD_FOLDER, surat_keluar.file_path))
    db.session.delete(surat_keluar)
    db.session.commit()
    current_app.logger.info(f"Admin user {current_user.username} deleted Surat Keluar: {surat_keluar.nomor_surat} (ID: {surat_id}) from {request.remote_addr}")
    flash('Surat Keluar berhasil dihapus!', 'success')
    return redirect(url_for('surat_keluar.list_surat_keluar'))

@surat_keluar_bp.route('/download/<int:surat_id>')
@login_required
@requires_role('admin') # Changed from roles_required
@owns_resource(SuratKeluar, 'surat_id') # Added owns_resource
def download_surat_keluar(surat_id):
    surat_keluar = SuratKeluar.query.get_or_404(surat_id)
    try:
        current_app.logger.info(f"User {current_user.username} downloaded Surat Keluar: {surat_keluar.nomor_surat} (ID: {surat_id}) from {request.remote_addr}")
        return send_from_directory(UPLOAD_FOLDER, surat_keluar.file_path, as_attachment=True)
    except FileNotFoundError:
        current_app.logger.error(f"File not found for Surat Keluar ID: {surat_id} (Path: {surat_keluar.file_path}) requested by {current_user.username} from {request.remote_addr}")
        flash('File tidak ditemukan.', 'danger')
        abort(404)
