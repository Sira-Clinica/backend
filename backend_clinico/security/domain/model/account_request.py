from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class AccountRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    requested_role: str = Field(nullable=False)  # 'medico' o 'enfermero'
    status: str = Field(default="pendiente")  # pendiente, aceptado, rechazado
    created_at: datetime = Field(default_factory=datetime.now)
    area :str = Field(default=None)
    motivo :str = Field(default=None)
