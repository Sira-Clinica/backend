
from datetime import datetime
from typing import Optional
from pydantic import Field
from sqlmodel import SQLModel

class PacienteInput(SQLModel):
   
   
    dni: str 
    nombre: str
    apellido: str
    edad: int
    genero: str  
    direccion: str
    telefono: str
    ocupacion: str
    fecha_nacimiento: str
    grupo_sanguineo: str
    seguro_social: str
    estado_civil: str
    alergias: str
    antedecentes_medicos: str
    antecedentes_familiares: str
    