from datetime import timedelta
import secrets
import base64
import os

from pydantic import BaseSettings
from cryptography.hazmat.backends import default_backend  # type: ignore
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes  # type: ignore
from cryptography.hazmat.primitives.padding import PKCS7  # type: ignore
from fastapi_jwt_auth import AuthJWT  # type: ignore
from schemas.authSchemas import TokenRequest
from .tokenConfig import TokenConfig


# JWT Settings, inheriting from BaseSettings with .env support
class SettingsJWT(BaseSettings):
    authjwt_secret_key: str = TokenConfig.SECRET_KEY
    authjwt_algorithm: str = "RS256"
    authjwt_public_key: str = TokenConfig.PUBLIC_KEY
    authjwt_private_key: str = TokenConfig.PRIVATE_KEY
    authjwt_token_location: list = ["headers"]
    authjwt_access_token_expires: timedelta = timedelta(
        minutes=TokenConfig.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)
    authjwt_cookie_csrf_protect: bool = True
    authjwt_cookie_samesite: str = "lax"

    class Config:
        env_file = ".env"  # Dukung penggunaan file .env


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

    def decrypter_aes_cbc(self, encrypted_data: str, key: str):
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode())

            # Ambil IV dari data yang diterima
            iv = encrypted_data[:16]
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
    def create_token(self, Authorize: AuthJWT, client_id: str):
        iv = self.generate_iv()
        key = self.generate_encryption_key()
        encrypted_client_id = self.encrypter_aes_cbc(client_id, key, iv)

        access_token = Authorize.create_access_token(
            subject=encrypted_client_id,
            expires_time=timedelta(days=1),
            algorithm="RS256",
        )
        return access_token
