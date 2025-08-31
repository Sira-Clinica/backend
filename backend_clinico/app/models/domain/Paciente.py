from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Paciente(SQLModel, table=True):
    __tablename__ = "pacientes"

    hce: str = Field(primary_key=True, index=True, max_length=20)
    dni: str = Field(index=True, unique=True, max_length=15)
    nombre: str
    apellido: str
    edad: int
    genero: str  # 'm' o 'f'
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    ocupacion: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    seguro_social: Optional[str] = None
    estado_civil: Optional[str] = None
    alergias: Optional[str] = None
    antedecentes_medicos: Optional[str] = None
    antecedentes_familiares: Optional[str] = None
    fecha_registro: datetime =  Field(default_factory=datetime.now)
    


