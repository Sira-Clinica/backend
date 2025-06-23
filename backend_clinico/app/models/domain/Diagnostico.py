from typing import Optional
from sqlmodel import SQLModel, Field

class Diagnostico(SQLModel, table=True):
    __tablename__ = "diagnosticos"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    dni: Optional[str] = Field(default=None, max_length=500)
    temperatura: float
    edad: int
    f_card: int
    f_resp: int
    talla: float
    peso: float
    genero: str  # 'm' o 'f'
    motivo_consulta: Optional[str] = Field(default=None, max_length=500)
    examenfisico: Optional[str] = Field(default=None, max_length=500)
    resultado: Optional[str] = Field(default=None, max_length=100)
