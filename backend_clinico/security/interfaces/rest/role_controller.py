from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend_clinico.security.domain.model.role import Role
from backend_clinico.security.application.role_service import RoleService
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.role_repository import RoleRepository
from backend_clinico.security.infrastructure.auth_dependencies import get_db, get_current_user

router_role = APIRouter(prefix="/roles", tags=["Roles"])


@router_role.get("/", summary="Listar roles")
def listar_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    role_repo = RoleRepository()
    role_service = RoleService(role_repo)
    return role_service.get_all_roles(db)



@router_role.post("/", summary="Crear nuevo rol")
def crear_rol(
    role: Role,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    role_repo = RoleRepository()
    role_service = RoleService(role_repo)
    return role_service.create_role(db, role)

