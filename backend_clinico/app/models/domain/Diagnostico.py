from typing import Optional
from sqlmodel import SQLModel, Field

class Diagnostico(SQLModel, table=True):
    __tablename__ = "diagnosticos"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    consulta_id: Optional[int] = Field(default=None, foreign_key="consultas.id")
    dni: Optional[str] = Field(default=None, max_length=500)
    temperatura: float
    edad: int
    f_card: int
    f_resp: int
    talla: float
    peso: float
    genero: str 
    motivo_consulta: Optional[str] = Field(default=None, max_length=500)
    examenfisico: Optional[str] = Field(default=None, max_length=500)
    indicaciones:Optional[str] = Field(default=None, max_length=500)
    medicamentos:Optional[str] = Field(default=None, max_length=500)
    notas:Optional[str] = Field(default=None, max_length=500)
    resultado: Optional[str] = Field(default=None, max_length=100)
    imc: Optional[float] = Field(default=None)
