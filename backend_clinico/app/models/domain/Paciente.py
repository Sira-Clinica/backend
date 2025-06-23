from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Paciente(SQLModel, table=True):
    __tablename__ = "pacientes"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    dni: str = Field(index=True, unique=True, max_length=15)
    nombre: str
    apellido: str
    edad: int
    genero: str  # 'm' o 'f'
    direccion: Optional[str] = None
    telefono: Optional[str] = None


