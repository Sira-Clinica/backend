

from pydantic import BaseModel
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role_id: int



class TokenData(BaseModel):
    username: Optional[str] = None
