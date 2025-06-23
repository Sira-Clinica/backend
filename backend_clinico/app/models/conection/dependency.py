

from fastapi import Depends
from sqlmodel import Session
from typing import Generator

from backend_clinico.app.models.conection.conection import get_session

def get_db() -> Generator[Session, None, None]:
    with get_session() as session:
        yield session
