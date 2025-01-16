from pydantic import BaseModel


class TokenRequest(BaseModel):
    client_id: str
