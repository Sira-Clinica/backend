from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend_clinico.app.models.conection.conection import get_session
from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.security.application.profile_service import ProfileService
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.profile_repository import  ProfileRepository
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user
from backend_clinico.security.resource.request.profile_update_null import ProfileUpdateNullInput

router_profile = APIRouter(prefix="/profiles", tags=["Profiles"])


def verificar_permisos(current_user: User):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

@router_profile.patch("/{user_id}/update-null-fields")
def update_null_profile_fields(
    user_id: int, 
    data: ProfileUpdateNullInput, 
    db: Session = Depends(get_session)
):
    service = ProfileService(ProfileRepository())
    
    try:
        updated_profile = service.update_profile_fields(db, user_id, data)
    except ValueError as e:
        # Este error viene de cuando se intenta actualizar un campo bloqueado
        raise HTTPException(status_code=400, detail=str(e))

    if not updated_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "message": "Campos actualizados correctamente (solo los permitidos se modificaron)",
        "data": updated_profile
    }




@router_profile.get("/{user_id}", summary="Obtener perfil por ID de usuario")
def get_profile_by_user_id(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    service = ProfileService(ProfileRepository())
    profile = service.get_profile_by_user_id(db, user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"user_id": user_id, "profile": profile}