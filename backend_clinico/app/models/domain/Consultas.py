from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field




class Consultas(SQLModel, table=True):
    __tablename__ = "consultas"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    paciente_hce: Optional[str] = Field(default=None, foreign_key="pacientes.hce")
    paciente_nombre: Optional[str]= None
    paciente_apelido: Optional[str]= None
    dni: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default="En espera", max_length=50)  
    user_fullname: Optional[str] = Field(default=None)
    anio:Optional[int] = Field(default=None)
    mes:Optional[int] = Field(default=None)
    dia:Optional[int] = Field(default=None)
    hora:Optional[int] = Field(default=None)
    minuto:Optional[int] = Field(default=None)


