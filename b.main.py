from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from auth.dataConfig import SafeConfig, TokenRequest
from fastapi_jwt_auth import AuthJWT  # type: ignore
import base64

app = FastAPI(
    title="Authentication | Fast API",
    summary="Abdi Bakti Authentication API",
    version="0.1",
)

safe_config = SafeConfig()


@app.post("/create-token", summary="Create Token JWT")
async def create_token(payload: TokenRequest, Authorize: AuthJWT = Depends()):
    try:
        # Create the token using SafeConfig and return it
        token = safe_config.create_token(Authorize, payload.client_id)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create token: {str(e)}")


@app.post("/generate-iv", summary="Generate IV")
async def generate_iv():
    iv = safe_config.generate_iv()
    return {"iv": base64.b64encode(iv.encode()).decode("utf-8"), "iv_hex": iv}


@app.post("/generate-client", summary="Generate Client ID")
async def generate_client():
    client_id, secret_key = safe_config.generate_client_id()
    return {"client_id": client_id, "secret_key": secret_key}


@app.post("/encrypter", summary="Encrypter AES")
async def encrypter_aes(data: str):
    try:
        encrypted_text = safe_config.encrypter_aes_cbc(data)
        return {"encrypted_text": encrypted_text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encryption failed: {str(e)}")


@app.post("/decrypter", summary="Decrypter AES")
async def decrypter_aes(encrypted_data: str):
    try:
        decrypted_data = safe_config.decrypter_aes_cbc(encrypted_data)
        return {"decrypted_text": decrypted_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decrypt data: {str(e)}")
