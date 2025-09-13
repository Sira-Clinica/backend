from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import SQLModel

from backend_clinico.app.models.conection.conection import engine, get_session
from backend_clinico.security.application.password_utils import hash_password
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.model.role import Role
from backend_clinico.security.domain.repository.role_repository import RoleRepository
from backend_clinico.app.interfaces.api import routes
from backend_clinico.security.domain.repository.user_repository import UserRepository
from backend_clinico.app.core.config import settings



def init_roles():
    db = get_session()
    role_repo = RoleRepository()
    roles = ["admin", "medico", "enfermero"]
    for role_name in roles:
        if not role_repo.get_by_name(db, role_name):
            role_repo.create(db, Role(name=role_name))

def init_admin_user():
    db = get_session()
    user_repo = UserRepository()
    role_repo = RoleRepository()

    # Obtener el rol admin
    admin_role = role_repo.get_by_name(db, "admin")
    if not admin_role:
        print("Rol 'admin' no encontrado. No se puede crear el usuario admin.")
        return

    # Verificar si ya existe el admin
    existing_admin = user_repo.get_by_username(db, settings.initial_admin_username)
    if existing_admin:
        print(f"Usuario admin '{settings.initial_admin_username}' ya existe.")
        return

    # Crear usuario admin con datos desde .env
    admin_user = User(
        username=settings.initial_admin_username,
        email=settings.initial_admin_email,
        full_name=settings.initial_admin_full_name,
        hashed_password=hash_password(settings.initial_admin_password),
        enabled=True,
        role_id=admin_role.id,
        area="Administración"  # Puedes poner otro valor si quieres que también venga de .env
    )
    user_repo.create(db, admin_user)
    print("Usuario admin creado por defecto con credenciales:")
    print(f"Usuario: {settings.initial_admin_username} / Contraseña: {settings.initial_admin_password}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    SQLModel.metadata.create_all(engine)
    init_roles()
    init_admin_user()
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
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
