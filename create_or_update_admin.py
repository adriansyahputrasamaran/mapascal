from app import create_app, db
from app.models import User
from datetime import datetime

app = create_app()
app.app_context().push()

username = 'admin'
password = 'admin123'
nama_lengkap = 'Administrator'
role = 'admin'

admin_user = User.query.filter_by(username=username).first()

if admin_user:
    admin_user.set_password(password)
    admin_user.nama_lengkap = nama_lengkap
    admin_user.role = role
    admin_user.updated_at = datetime.utcnow()
    db.session.commit()
    print(f"Admin user '{username}' updated successfully. Password set to '{password}'.")
else:
    new_admin = User(username=username, nama_lengkap=nama_lengkap, role=role)
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()
    print(f"Admin user '{username}' created successfully. Password set to '{password}'.")
