from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from auth.dataConfig import SafeConfig
from schemas.authSchemas import TokenRequest
from auth.tokenConfig import TokenConfig
from fastapi_jwt_auth import AuthJWT  # type: ignore
from fastapi_jwt_auth.exceptions import AuthJWTException  # type: ignore
import base64
from routes import menuRoutes
import logging
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logging.basicConfig(
    filename="log/Server/server.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Authentication | Fast API",
    summary="Abdi Bakti Authentication API",
    version="0.1",
)

safe_config = SafeConfig()
security = HTTPBearer()


# Menangani error pada JWT
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.post("/create-token", summary="Create Token JWT", tags=["Auth"])
async def create_token(payload: TokenRequest, Authorize: AuthJWT = Depends()):
    try:
        token = safe_config.create_token(
            Authorize, payload.client_id, payload.key, payload.iv
        )
        logging.info(f"Token berhasil dibuat: {token}")
        return {"access_token": token}

    except Exception as e:
        logging.error(f"Error membuat token: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Gagal membuat token: {str(e)}")


@app.get("/generate-aes", summary="Generate IV", tags=["Menu Generator"])
async def generate_iv():
    aes_key, aes_iv = safe_config.generate_aes_key_and_iv()

    logging.info(f"AES KEY // {aes_key} //")
    logging.info(f"AES IV // {aes_iv} //")
    return {"iv": aes_iv, "aes_key": aes_key}


# Endpoint untuk menghasilkan Client ID dan Secret Key
@app.post("/generate-client", summary="Generate Client ID", tags=["Menu Generator"])
async def generate_client():
    client_id, secret_key = safe_config.generate_client_id()
    logging.info(f"Generate Client ID // {client_id} //")
    logging.info(f"Generate Secret Key // {secret_key} //")
    return {"client_id": client_id, "secret_key": secret_key}


# Endpoint untuk mengenkripsi data menggunakan AES CBC
@app.post("/encrypter", summary="Encrypter AES", tags=["Menu Encryption"])
async def encrypter_aes(data: str):
    try:
        encrypted_text = safe_config.encrypter_aes_cbc(
            data, TokenConfig.AES_KEY, TokenConfig.AES_IV
        )
        return {"encrypted_text": encrypted_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encryption failed: {str(e)}")


# Endpoint untuk mendekripsi data yang telah dienkripsi
@app.post("/decrypter", summary="Decrypter AES", tags=["Menu Encryption"])
async def decrypter_aes(encrypted_data: str):
    try:
        decrypted_data = safe_config.decrypter_aes_cbc(encrypted_data)
        return {"decrypted_text": decrypted_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decrypt data: {str(e)}")


app.include_router(menuRoutes, prefix="/menu", tags=["Menu Management Data"])
