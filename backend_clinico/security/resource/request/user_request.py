
from pydantic import BaseModel, EmailStr, constr
from typing import Annotated
from pydantic import StringConstraints

class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role_name: str  # nombre del rol a asignar


class UserUpdateRequest(BaseModel):
    full_name: str
    email: EmailStr




class UserPasswordChangeRequest(BaseModel):
    old_password: Annotated[str, StringConstraints(min_length=6)]
    new_password: Annotated[str, StringConstraints(min_length=6)]