

from sqlmodel import SQLModel, create_engine, Session
from backend_clinico.app.core.config import settings

DATABASE_URL = settings.database_url


engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    return Session(engine)