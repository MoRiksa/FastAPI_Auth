from datetime import timedelta
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Validasi kunci RSA
try:
    private_key_path = os.getenv("PRIVATE_KEY")
    public_key_path = os.getenv("PUBLIC_KEY")
    if not private_key_path or not public_key_path:
        raise ValueError("PRIVATE_KEY atau PUBLIC_KEY tidak ditemukan.")

    with open(private_key_path, "r") as private_file:
        private_key = private_file.read()
    with open(public_key_path, "r") as public_file:
        public_key = public_file.read()
except Exception as e:
    raise FileNotFoundError(f"Error membaca kunci RSA: {str(e)}")


# Token Configuration
class TokenConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    PUBLIC_KEY = public_key
    PRIVATE_KEY = private_key
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    AES_KEY = os.getenv("AES_KEY")
    AES_IV = os.getenv("AES_IV")

    if not all([SECRET_KEY, AES_KEY, AES_IV]):
        raise ValueError("SECRET_KEY, AES_KEY, atau AES_IV tidak valid.")
