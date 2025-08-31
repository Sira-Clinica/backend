from sqlmodel import SQLModel, Field
from datetime import datetime

class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message: str
    fecha_registro: datetime =  Field(default_factory=datetime.now)
