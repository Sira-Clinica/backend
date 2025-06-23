from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from backend_clinico.app.models.conection.conection import engine, get_session
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.model.role import Role
from backend_clinico.security.domain.repository.role_repository import RoleRepository
from backend_clinico.app.interfaces.api import routes



def init_roles():
    db = get_session()
    role_repo = RoleRepository()
    roles = ["admin", "medico", "enfermero"]
    for role_name in roles:
        if not role_repo.get_by_name(db, role_name):
            role_repo.create(db, Role(name=role_name))



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    SQLModel.metadata.create_all(engine)
    init_roles()
    yield



app = FastAPI(title="API Diagnóstico Clínico", lifespan=lifespan)


origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "https://tudominio.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,     
    allow_methods=["*"],        
    allow_headers=["*"],         
)


app.include_router(routes.router)


@app.get("/")
def root():
    return {"message": "Diagnóstico Clínico API corriendo correctamente"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
