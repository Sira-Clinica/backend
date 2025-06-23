from __future__ import annotations
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class VitalSign(SQLModel, table=True):
    __tablename__ = "vitalsigns"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    paciente_id: Optional[int] = Field(default=None, foreign_key="pacientes.id")
    temperatura: float
    edad: int
    f_card: int
    f_resp: int
    talla: float
    peso: float
    genero: str  # 'm' o 'f'

