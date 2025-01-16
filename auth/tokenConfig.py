from datetime import timedelta
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env dari satu folder di atas 'auth'
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Mengambil path private dan public key dari .env
private_key_path = os.getenv("PRIVATE_KEY")
public_key_path = os.getenv("PUBLIC_KEY")

# Validasi jika path tidak ditemukan
if not private_key_path or not public_key_path:
    raise ValueError("PRIVATE_KEY atau PUBLIC_KEY tidak ditemukan di file .env")

# Membaca file kunci dengan error handling
try:
    with open(private_key_path, "r") as private_file:
        private_key = private_file.read()
        print("Private key successfully read.")
    with open(public_key_path, "r") as public_file:
        public_key = public_file.read()
        print("Public key successfully read.")
except FileNotFoundError:
    raise FileNotFoundError(
        "Private or Public key file not found in the specified path."
    )


class TokenConfig:
    SECRET_KEY = "fb7d0dc95422d281fa9f11bc5827624c07d7aa0f34f1cd60f3b7c138f4e58670"
    PUBLIC_KEY = public_key  # Memuat isi file public key
    PRIVATE_KEY = private_key  # Memuat isi file private key
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    CLIENT_ID = "df31c19da7f89fb147d75c7c992a3f6c"
    IV = "49991a90bf73983a15a4e4766925f91e"
