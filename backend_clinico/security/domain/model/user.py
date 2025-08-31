from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy.orm import Mapped
from backend_clinico.security.domain.model.role import Role

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(nullable=False, unique=True)
    email: str = Field(nullable=False, unique=True)
    full_name: str = Field(nullable=False)
    hashed_password: str = Field(nullable=False)
    enabled: Optional[bool] = Field(default=False)
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    area: Optional[str] = Field(default=None)
    ultimo_accesso: Optional[datetime] = Field(default=None)    


   
