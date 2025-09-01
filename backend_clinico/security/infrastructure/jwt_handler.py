from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from backend_clinico.app.core.config import settings

ACCES_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
SECRET_KEY = settings.secret_key
ALOGRITHM = settings.algorithm

    
    


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALOGRITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALOGRITHM])
        return decoded_token
    except JWTError as e:
        raise JWTError("Token inválido") from e
