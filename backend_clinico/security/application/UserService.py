from sqlmodel import Session
from typing import List

from backend_clinico.security.application.password_utils import hash_password, verify_password
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.user_repository import UserRepository
from backend_clinico.security.resource.request.user_request import UserUpdateRequest


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_all_users(self, db: Session) -> List[User]:
        return self.user_repo.get_all(db)

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        return user

    def delete_user(self, db: Session, user_id: int) -> dict:
        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        self.user_repo.delete(db, user)
        return {"message": "Usuario eliminado correctamente"}
    
    def update_user(self, db: Session, user_id: int, data: UserUpdateRequest) -> User:
        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        user.full_name = data.full_name
        user.email = data.email
        return self.user_repo.update(db, user)

    def change_password(self, db: Session, user_id: int, old_pass: str, new_pass: str) -> dict:
        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        if not verify_password(old_pass, user.hashed_password):
            raise ValueError("Contraseña actual incorrecta")
        user.hashed_password = hash_password(new_pass)
        self.user_repo.update(db, user)
        return {"message": "Contraseña actualizada correctamente"}