
from sqlmodel import SQLModel

class VitalSignInput(SQLModel):
    temperatura: float
    edad: int
    f_card: int
    f_resp: int
    talla: float
    peso: float
    genero: str
    dni: str
    