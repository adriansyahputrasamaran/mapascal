from werkzeug.security import check_password_hash

hash1 = "pbkdf2:sha256:600000$Busr2uM9032NvRkj$ed6320a0c9db437780eca64ef536a1636e18337b4bcad7752cc7106171ae991a"
hash2 = "scrypt:32768:8:1$A2ethKntgS3cVeEx$91d1888c297aee14328f947323c3d72e16232d50866387de02ecbe39aeb86c9417cb8333a3c409880ed89d74c7e43271a00018e8c5b8a4cd61adc3ded35ba050"

plain = "admin123"  # ganti dengan password biasa yang kamu pakai

print("hash1 ok?", check_password_hash(hash1, plain))
print("hash2 ok?", check_password_hash(hash2, plain))