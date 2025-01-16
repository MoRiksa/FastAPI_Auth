from datetime import timedelta
import secrets
import base64
import os

from pydantic import BaseSettings
from cryptography.hazmat.backends import default_backend  # type: ignore
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # type: ignore
from cryptography.hazmat.primitives.padding import PKCS7  # type: ignore
from fastapi_jwt_auth import AuthJWT  # type: ignore
from .tokenConfig import TokenConfig


# JWT Settings, inheriting from BaseSettings with .env support
class SettingsJWT(BaseSettings):
    authjwt_algorithm: str = "RS256"  # Algoritma asimetris
    authjwt_public_key: str = TokenConfig.PUBLIC_KEY  # Kunci publik dalam format PEM
    authjwt_private_key: str = TokenConfig.PRIVATE_KEY  # Kunci privat dalam format PEM
    authjwt_token_location: list = ["headers"]
    authjwt_access_token_expires: timedelta = timedelta(minutes=15)
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_samesite: str = "lax"

    class Config:
        env_file = ".env"


# Ensure the correct loading of the settings
@AuthJWT.load_config
def get_config():
    return SettingsJWT()


# Encryption logic in a separate class
class SafeConfig:

    def generate_client_id(self):
        client_id = secrets.token_hex(16)
        secret_key = secrets.token_hex(32)
        return client_id, secret_key

    def generate_aes_key_and_iv(self):
        aes_key = secrets.token_hex(32)  # 32 bytes key for AES-256
        aes_iv = secrets.token_hex(16)  # 16 bytes IV
        return aes_key, aes_iv

    def generate_encryption_key(self):
        return os.urandom(32).hex()

    def generate_iv(self):
        return os.urandom(16).hex()

    def encrypter_aes_cbc(self, data: str, key: str, iv: str) -> str:
        padder = PKCS7(128).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        cipher = Cipher(
            algorithms.AES(bytes.fromhex(key)),
            modes.CBC(bytes.fromhex(iv)),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.urlsafe_b64encode(bytes.fromhex(iv) + encrypted_data).decode()

    def decrypter_aes_cbc(self, encrypted_data: str):
        key = TokenConfig.AES_KEY
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode())

            # Ambil IV dari data yang diterima
            iv = bytes.fromhex(TokenConfig.AES_IV)
            encrypted_data = encrypted_data[16:]

            cipher = Cipher(
                algorithms.AES(bytes.fromhex(key)),
                modes.CBC(iv),
                backend=default_backend(),
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

            # Unpadding dengan PKCS7
            unpadder = PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            return data.decode()
        except ValueError:
            return "Error: Invalid padding or corrupted data"
        except Exception as e:
            return f"Error during decryption: {str(e)}"

    # Fungsi untuk membuat token JWT dengan kunci RSA
    def create_token(self, Authorize, client_id: str, key: str, iv: str) -> str:
        try:
            # Skip client validation
            access_token = Authorize.create_access_token(subject=client_id)
            return access_token
        except Exception as e:
            raise Exception(f"Error in create_token: {str(e)}")
