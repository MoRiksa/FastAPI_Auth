from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from auth.dataConfig import SafeConfig, TokenRequest
from fastapi_jwt_auth import AuthJWT  # type: ignore
from fastapi_jwt_auth.exceptions import AuthJWTException  # type: ignore
import base64

app = FastAPI(
    title="Authentication | Fast API",
    summary="Abdi Bakti Authentication API",
    version="0.1",
)

safe_config = SafeConfig()


# Menangani error pada JWT
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


# Endpoint untuk membuat token JWT
@app.post("/create-token", summary="Create Token JWT", tags=["Menu Generator"])
async def create_token(payload: TokenRequest, Authorize: AuthJWT = Depends()):
    try:
        token = safe_config.create_token(Authorize, payload.client_id)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create token: {str(e)}")


# Endpoint dengan proteksi autentikasi
@app.get("/periksa-auth", summary="Periksa Authentication Token", tags=["Menu Auth"])
def protected_endpoint(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()  # Memastikan token valid
        current_user = Authorize.get_jwt_subject()
        return {"message": f"Halo, {current_user}. Kamu Sudah Memilikii Authentikasi!"}
    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Belum Memiliki Authentikasi!: {str(e)}"
        )


# Endpoint untuk menghasilkan IV
@app.post("/generate-iv", summary="Generate IV", tags=["Menu Generator"])
async def generate_iv():
    iv = safe_config.generate_iv()
    return {"iv": base64.b64encode(iv.encode()).decode("utf-8"), "iv_hex": iv}


# Endpoint untuk menghasilkan Client ID dan Secret Key
@app.post("/generate-client", summary="Generate Client ID")
async def generate_client():
    client_id, secret_key = safe_config.generate_client_id()
    return {"client_id": client_id, "secret_key": secret_key}


# Endpoint untuk mengenkripsi data menggunakan AES CBC
@app.post("/encrypter", summary="Encrypter AES")
async def encrypter_aes(data: str):
    try:
        encrypted_text = safe_config.encrypter_aes_cbc(data)
        return {"encrypted_text": encrypted_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encryption failed: {str(e)}")


# Endpoint untuk mendekripsi data yang telah dienkripsi
@app.post("/decrypter", summary="Decrypter AES")
async def decrypter_aes(encrypted_data: str):
    try:
        decrypted_data = safe_config.decrypter_aes_cbc(encrypted_data)
        return {"decrypted_text": decrypted_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decrypt data: {str(e)}")
