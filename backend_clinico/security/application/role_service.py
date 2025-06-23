from requests import Session
from backend_clinico.security.domain.model.role import Role
from backend_clinico.security.domain.repository.role_repository import RoleRepository




class RoleService:

    def __init__(self, role_repo: RoleRepository):
        self.role_repo = role_repo

    def get_all_roles(self, db: Session) -> list[Role]:
        return self.role_repo.get_all(db)

    def get_role_by_name(self, db: Session, name: str) -> Role:
        role = self.role_repo.get_by_name(db, name)
        if not role:
            raise ValueError("Rol no encontrado")
        return role

    def create_role(self, db: Session, role: Role) -> Role:
        return self.role_repo.create(db, role)
