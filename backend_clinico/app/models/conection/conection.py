

from sqlmodel import SQLModel, create_engine, Session


DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/clinica_db"

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    return Session(engine)