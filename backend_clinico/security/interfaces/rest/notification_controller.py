from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.security.application.notification_service import NotificationService
from backend_clinico.security.domain.repository.notification_repository import NotificationRepository
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user

router_notification = APIRouter(prefix="/notifications", tags=["Notificaciones"])

def verificar_admin(current_user: User):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

@router_notification.get("/", summary="Mostrar todas las notificaciones (solo admin)")
def mostrar_todo_notification(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_admin(current_user)
    service = NotificationService(NotificationRepository())
    notificaciones = service.mostrar_todo(db)
    return {"notificaciones": notificaciones}

@router_notification.delete("/{notif_id}", summary="Eliminar notificación por ID (solo admin)")
def eliminar_notification(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_admin(current_user)
    service = NotificationService(NotificationRepository())
    try:
        service.eliminar_por_id(db, notif_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f"Notificación con id {notif_id} eliminada correctamente"}

