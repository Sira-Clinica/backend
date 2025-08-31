from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend_clinico.security.application.auth_service import AuthService
from backend_clinico.security.application.password_utils import verify_password

from backend_clinico.security.domain.model.auth_token import TokenResponse
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.user_repository import UserRepository
from backend_clinico.security.resource.request.user_request import UserLogin, UserRegister
from backend_clinico.security.infrastructure.auth_dependencies import get_db
from backend_clinico.security.infrastructure.jwt_handler import create_access_token
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user

router_auth = APIRouter(prefix="/auth", tags=["Autenticación"])


@router_auth.post("/login", summary="Iniciar sesión y obtener token")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(UserRepository()) 
    user = auth_service.authenticate_user(db, credentials.username, credentials.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Actualizar el último acceso
    user.ultimo_accesso = datetime.now()
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.username, "role": user.role_id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        role_id=user.role_id
    )




@router_auth.post("/register", summary="Registrar nuevo usuario")
def register(data: UserRegister, 
             db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)
             ):

    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")
    existing = AuthService.user_exists(db, data.username, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nombre de usuario o correo ya registrado"
        )
    user = AuthService.register_user(db, data)
    return {"message": "Usuario registrado correctamente", "user": user}


@router_auth.get("/me", summary="Obtener información del usuario actual")
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
