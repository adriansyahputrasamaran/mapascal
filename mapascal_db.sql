-- mapascal_db.sql

-- Drop database if it exists and create a new one
DROP DATABASE IF EXISTS mapascal;
CREATE DATABASE mapascal;
USE mapascal;

-- Table for users
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nama_lengkap VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'admin' or 'anggota'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table for incoming mail (surat_masuk)
CREATE TABLE surat_masuk (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomor_surat VARCHAR(100) UNIQUE NOT NULL,
    asal_surat VARCHAR(100) NOT NULL,
    tanggal_terima DATE NOT NULL,
    perihal TEXT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_by_user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by_user_id) REFERENCES users(id)
);

-- Table for outgoing mail (surat_keluar)
CREATE TABLE surat_keluar (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nomor_surat VARCHAR(100) UNIQUE NOT NULL,
    tujuan_surat VARCHAR(100) NOT NULL,
    tanggal_surat DATE NOT NULL,
    perihal TEXT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    uploaded_by_user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by_user_id) REFERENCES users(id)
);

-- Insert default admin user
INSERT INTO users (username, password_hash, nama_lengkap, role) VALUES
('admin', 'scrypt:32768:8:1$YThjsEJXeD1dEFG0$78905239d819271870def41646f4fecedb60fdab7b62363fbf92ab32099a7c9dd16fde2404bbf7f3c5ac1be1ef95892c666029fa0465a7fd2519e19940dfbc3f', 'Admin MAPASCAL', 'admin');
