from __future__ import annotations
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy.orm import Mapped


class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)

 


