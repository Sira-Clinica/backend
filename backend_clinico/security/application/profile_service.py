from sqlmodel import Session
from backend_clinico.security.domain.repository.profile_repository import ProfileRepository
from backend_clinico.security.resource.request.profile_update_null import ProfileUpdateNullInput


class ProfileService:
    def __init__(self, repository: ProfileRepository):
        self.repository = repository

    def update_profile_fields(self, db: Session, user_id: int, data: ProfileUpdateNullInput):
        """
        Actualiza los campos de un perfil.
        - Los campos marcados como no editables no se actualizarán si ya tienen un valor.
        - Los demás campos sí se pueden actualizar.
        """
        return self.repository.update_null_fields(
            db,
            user_id,
            data.dict(exclude_unset=True)
        )
    
    def get_profile_by_user_id(self, db: Session, user_id: int):
        """
        Obtiene un perfil por el ID de usuario.
        Retorna None si no existe.
        """
        return self.repository.get_by_user_id(db, user_id)
