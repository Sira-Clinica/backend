from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message: str
    fecha_registro: datetime =  Field(default_factory=lambda: datetime.now(timezone.utc))
