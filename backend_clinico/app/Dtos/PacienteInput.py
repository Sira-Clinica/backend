
from typing import Optional
from sqlmodel import SQLModel

class PacienteInput(SQLModel):
   
   
    dni: str 
    nombre: str
    apellido: str
    edad: int
    genero: str  # 'm' o 'f'
    direccion: Optional[str] = None
    telefono: Optional[str] = None