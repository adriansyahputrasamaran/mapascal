import os
import sys
from app import create_app, db
from app.models import User

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = create_app()

def force_activate_admin():
    """
    Finds the user with username 'admin' and forcefully sets their
    is_active status to True.
    """
    with app.app_context():
        admin_username = 'admin'
        print(f"--- Mencari user: '{admin_username}' ---")
        
        try:
            admin_user = User.query.filter_by(username=admin_username).first()

            if not admin_user:
                print(f"HASIL: GAGAL. User '{admin_username}' tidak ditemukan di database.")
                print("Silakan jalankan 'python create_or_update_admin.py' terlebih dahulu untuk membuat akun admin.")
                return

            if admin_user.is_active:
                print(f"HASIL: SUDAH AKTIF. User '{admin_username}' sudah dalam status aktif.")
                return

            # Force activation
            admin_user.is_active = True
            db.session.commit()
            
            # Verify the change
            refreshed_user = User.query.get(admin_user.id)
            if refreshed_user.is_active:
                print(f"HASIL: SUKSES! User '{admin_username}' telah berhasil diaktifkan.")
            else:
                print("HASIL: GAGAL. Gagal memverifikasi perubahan status di database.")

        except Exception as e:
            db.session.rollback()
            print(f"Terjadi error saat operasi database: {e}")

if __name__ == '__main__':
    force_activate_admin()
