from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class VitalSign(SQLModel, table=True):
    __tablename__ = "vitalsigns"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    paciente_hce: Optional[str] = Field(default=None, foreign_key="pacientes.hce")
    dni: Optional[str] = Field(default= None,  unique=True)
    temperatura: float
    edad: Optional[int] = None
    f_card: Optional[int]
    f_resp: Optional[int]
    talla: Optional[float]
    peso: Optional[float]
    genero: Optional[str] = None
    imc: Optional[float] = None
    fecha_registro: Optional[datetime]= None

