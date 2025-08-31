
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional
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
    area: Optional[str] = None

class UserUpdateRequest(BaseModel):
    full_name: str
    email: EmailStr




class UserPasswordChangeRequest(BaseModel):
    old_password: Annotated[str, StringConstraints(min_length=6)]
    new_password: Annotated[str, StringConstraints(min_length=6)]



class CreateUserFromRequestInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str  # Ejemplo: "medico", "paciente", "admin"
    area: Optional[str] = None  
    motivacion: Optional[str] = None  # Documento nacional de identidad (si aplica)