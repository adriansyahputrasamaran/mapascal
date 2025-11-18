import os
import sys
import getpass
from flask import Flask
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

app = create_app()

def create_or_update_admin():
    """
    A command-line script to securely create or update an admin user.
    """
    with app.app_context():
        print("--- Script Pembuatan/Update Admin ---")
        
        try:
            # 1. Get Admin Username
            username = input("Masukkan username untuk admin: ").strip()
            if not username:
                print("Error: Username tidak boleh kosong.")
                return

            # 2. Check if admin user already exists
            admin_user = User.query.filter_by(username=username).first()

            # 3. Get Password securely
            password = getpass.getpass("Masukkan password baru untuk admin: ")
            if not password:
                print("Error: Password tidak boleh kosong.")
                return
            
            password_confirm = getpass.getpass("Konfirmasi password baru: ")
            if password != password_confirm:
                print("Error: Password tidak cocok.")
                return

            if admin_user:
                # --- UPDATE EXISTING ADMIN ---
                print(f"Admin dengan username '{username}' sudah ada. Melakukan update...")
                admin_user.set_password(password)
                admin_user.is_active = True  # Fix: Ensure admin is always active
                db.session.commit()
                print(f"Password dan status aktif untuk admin '{username}' berhasil diperbarui.")
            else:
                # --- CREATE NEW ADMIN ---
                print(f"Membuat admin baru dengan username '{username}'...")
                nama_lengkap = input("Masukkan nama lengkap untuk admin: ").strip()
                if not nama_lengkap:
                    print("Error: Nama lengkap tidak boleh kosong.")
                    return

                # The 'nia' field is non-nullable. We'll use a placeholder for admins.
                nia_placeholder = f"ADMIN-{username.upper()}"

                new_admin = User(
                    username=username,
                    nama_lengkap=nama_lengkap,
                    nia=nia_placeholder,  # Satisfy the non-nullable constraint
                    role='admin',
                    is_active=True  # Fix: Ensure new admin is created as active
                )
                new_admin.set_password(password)
                
                db.session.add(new_admin)
                db.session.commit()
                print(f"Admin '{username}' berhasil dibuat dan diaktifkan.")

        except Exception as e:
            db.session.rollback()
            print(f"Terjadi error: {e}")
            print("Operasi dibatalkan.")

if __name__ == '__main__':
    create_or_update_admin()
