

from typing import Optional
from sqlmodel import SQLModel

class ConsultaInput(SQLModel):
    status: str
    dni: str
    user_fullname_medic: str
    dia: int
    hora: int
    minuto:int



class UpdateStatusConsultaInput(SQLModel):
    status: str