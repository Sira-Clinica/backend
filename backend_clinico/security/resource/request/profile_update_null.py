from pydantic import BaseModel, Field
from typing import Optional, Dict
from sqlalchemy import Column, JSON

class ProfileUpdateNullInput(BaseModel):
    phone: Optional[str] = Field(default=None, max_length=20)
    description: Optional[str] = Field(default=None, max_length=500)
    cmp: Optional[str] = Field(default=None, max_length=20)
    consultorio: Optional[str] = Field(default=None, max_length=255)
    sede: Optional[str] = Field(default=None, max_length=255)
    experiencia: Optional[str] = Field(default=None, max_length=50)

    # Campos adicionales editables
    idiomas: Optional[str] = Field(default=None, max_length=255)
    redes: Optional[Dict[str, str]] = Field(default=None)
    formacion: Optional[Dict[str, str]] = Field(default=None)
    horarios: Optional[Dict[str, str]] = Field(default=None)

    class Config:
        orm_mode = True

