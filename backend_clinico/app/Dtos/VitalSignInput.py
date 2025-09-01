
from sqlmodel import SQLModel

class VitalSignInput(SQLModel):
    temperatura: float
    f_card: int
    f_resp: int
    talla: float
    peso: float
    dni: str

   
    