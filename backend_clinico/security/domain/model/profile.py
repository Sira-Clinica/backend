from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Text


class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)

    # Información personal y profesional
    full_name: str = Field(max_length=150, nullable=False)
    email: str = Field(max_length=120, nullable=False, unique=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    area: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None)
    cmp: Optional[str] = Field(default=None, max_length=50)
    consultorio: Optional[str] = Field(default=None, max_length=100)
    sede: Optional[str] = Field(default=None, max_length=255)
    experiencia: Optional[str] = Field(default=None, max_length=50)

    # Información adicional (usando Column JSON directamente)
    idiomas: Optional[str] = Field(default=None, max_length=255)
    redes: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    formacion: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    horarios: Optional[dict] = Field(default=None, sa_column=Column(JSON))



  

