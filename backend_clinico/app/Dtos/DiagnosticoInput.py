

from typing import Optional
from sqlmodel import SQLModel

class DiagnosticoInput(SQLModel):
    temperatura: float
    edad: int
    f_card: int
    f_resp: int
    talla: float
    peso: float
    genero: str
    motivo_consulta: Optional[str] = None
    examenfisico: Optional[str] = None
    imc: Optional[float] = None
