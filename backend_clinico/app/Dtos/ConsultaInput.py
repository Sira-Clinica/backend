

from typing import Optional
from sqlmodel import SQLModel

class ConsultaInput(SQLModel):
    dni: str
    user_fullname_medic: str
    dia: int
    hora: int
    minuto:int



class UpdateStatusConsultaInput(SQLModel):
    status: str



class UpdateEditStatusConsultaInput(SQLModel):
    edit_status: bool