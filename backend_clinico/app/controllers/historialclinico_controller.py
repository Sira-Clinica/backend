from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from backend_clinico.app.models.conection.dependency import get_db

from backend_clinico.app.models.repositories.historialclinico_repository import obtener_historial_por_dni
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user

historial_router = APIRouter(prefix="/historial", tags=["Historial Clínico"])

@historial_router.get("/{dni}", summary="Obtener historial clínico completo por DNI (doctor y admin)")
def obtener_historial_clinico(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

    historial = obtener_historial_por_dni(db, dni)
    if not historial:
        raise HTTPException(status_code=404, detail="Historial clínico no encontrado")

    return historial
