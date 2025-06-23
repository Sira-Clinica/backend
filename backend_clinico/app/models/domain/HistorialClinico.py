from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class HistorialClinico(SQLModel, table=True):
    __tablename__ = "historial_clinico"

    id: Optional[int] = Field(default=None, primary_key=True)
    paciente_dni: str
    paciente_nombre: str
    temperatura: float
    edad: int
    f_card: int
    f_resp: int
    talla: float
    peso: float
    genero: str
    motivo_consulta: str
    examenfisico: str
    resultado_diagnostico: str
    fecha_registro: datetime = Field(default_factory=datetime.utcnow)
