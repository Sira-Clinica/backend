
from fastapi import HTTPException, status
from sqlmodel import Session

from backend_clinico.security.domain.model.profile import Profile

from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.profile_repository import ProfileRepository
from backend_clinico.security.domain.repository.role_repository import RoleRepository
from backend_clinico.security.domain.repository.user_repository import UserRepository
from backend_clinico.security.infrastructure.jwt_handler import create_access_token
from backend_clinico.security.application.password_utils import hash_password, verify_password
from backend_clinico.security.domain.model.auth_token import TokenResponse
from backend_clinico.security.resource.request.user_request import UserRegister


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
   
    def authenticate_user(self, db: Session, username: str, password: str) -> User:
        user = self.user_repo.get_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )

        if not user.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario deshabilitado",
            )

        return user


    @staticmethod
    def user_exists(db: Session, username: str, email: str) -> bool:
        repo = UserRepository()
        return (
            repo.get_by_username(db, username) is not None
            or repo.get_by_email(db, email) is not None
        )
    
    @staticmethod
    def register_user(db: Session, data: UserRegister) -> User:
        user_repo = UserRepository()
        role_repo = RoleRepository()
        profile_repo = ProfileRepository()

        # Verificar que el rol exista
        role = role_repo.get_by_name(db, data.role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El rol especificado no existe"
            )

        # Crear el nuevo usuario
        new_user = User(
            username=data.username,
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            enabled=True,
            role_id=role.id
        )
        user_repo.create(db, new_user)

        # Crear el perfil con datos básicos (los demás quedan NULL)
        profile = Profile(
            user_id=new_user.id,
            full_name=data.full_name,
            email=data.email,
            phone=None,        # Se puede llenar luego
            area=data.area,    # Si viene desde el registro
            description=None,
            idiomas=None,
            redes=None,
            formacion=None,
            horarios=None,
            cmp=None,
            consultorio=None,
            sede=None,
            experiencia=None
        )
        profile_repo.create(db, profile)

        return new_user
