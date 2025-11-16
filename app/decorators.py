from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def requires_role(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Anda harus login untuk mengakses halaman ini.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role != role_name and current_user.role != 'admin':
                flash('Anda tidak memiliki izin untuk mengakses halaman ini.', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def owns_resource(model, id_param, owner_attr='uploaded_by_user_id'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Anda harus login untuk mengakses halaman ini.', 'warning')
                return redirect(url_for('auth.login'))

            resource_id = kwargs.get(id_param)
            if not resource_id:
                abort(400) # Bad request if ID is missing

            resource = model.query.get_or_404(resource_id)

            # Admin can always access
            if current_user.role == 'admin':
                return f(*args, **kwargs)

            # Check if the current user owns the resource
            if hasattr(resource, owner_attr) and getattr(resource, owner_attr) == current_user.id:
                return f(*args, **kwargs)
            else:
                flash('Anda tidak memiliki izin untuk mengakses sumber daya ini.', 'danger')
                abort(403)
        return decorated_function
    return decorator
