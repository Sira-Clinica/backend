from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel, EmailStr

from backend_clinico.security.domain.model.account_request import AccountRequest
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.account_request_repository import AccountRequestRepository
from backend_clinico.security.domain.repository.notification_repository import NotificationRepository
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user, get_db
from backend_clinico.security.application.password_utils import hash_password
from backend_clinico.security.domain.repository.user_repository import UserRepository, send_credentials_email
from backend_clinico.security.domain.repository.role_repository import RoleRepository
from backend_clinico.security.resource.request.user_request import CreateUserFromRequestInput

router_account = APIRouter(prefix="/account-requests", tags=["Solicitudes de cuenta"])

class AccountRequestInput(BaseModel):
    full_name: str
    email: EmailStr
    requested_role: str  # medico o enfermero
    area: str
    motivo: str

@router_account.post("/", summary="Enviar solicitud de creación de cuenta")
def enviar_solicitud(request: AccountRequestInput, db: Session = Depends(get_db)):
    if request.requested_role not in ["medico", "enfermero"]:
        raise HTTPException(status_code=400, detail="Solo médicos o enfermeros pueden solicitar cuenta.")

    # Crear la solicitud
    repo = AccountRequestRepository()
    nueva_solicitud = AccountRequest(
        full_name=request.full_name,
        email=request.email,
        requested_role=request.requested_role,
        area=request.area,
        motivo=request.motivo
    )
    solicitud_creada = repo.create(db, nueva_solicitud)

    # Crear la notificación
    notif_repo = NotificationRepository()
    message = f"Se ha enviado una nueva solicitud de credenciales  de {request.full_name} ({request.email})"
    notif_repo.create(db, message)

    return {"message": "Solicitud enviada correctamente", "solicitud": solicitud_creada}


@router_account.post("/{request_id}/approve", summary="Aprobar solicitud")
def aprobar_solicitud(
    request_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Solo admin puede aprobar
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    repo = AccountRequestRepository()
    solicitud = repo.get_by_id(db, request_id)
    if not solicitud or solicitud.status != "pendiente":
        raise HTTPException(status_code=404, detail="Solicitud no encontrada o ya procesada")

    # Cambiar estado a aprobado (pero aún no crear usuario)
    repo.update_status(db, solicitud, "aceptado")

    return {"message": "Solicitud aprobada. Ahora puede crearse el usuario."}



class ApproveRequestInput(BaseModel):
    username: str
    password: str  # contraseña temporal asignada por el admin

@router_account.post("/{request_id}/create-user", summary="Crear usuario desde solicitud aprobada")
def crear_usuario_desde_solicitud(
    request_id: int,
    data: ApproveRequestInput,  # Usamos el modelo correcto
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Validar permisos (solo admin)
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    # Buscar la solicitud
    repo = AccountRequestRepository()
    solicitud = repo.get_by_id(db, request_id)
    if not solicitud or solicitud.status != "aceptado":
        raise HTTPException(status_code=400, detail="La solicitud no ha sido aprobada aún")

    # Asignar rol correspondiente
    role_repo = RoleRepository()
    role = role_repo.get_by_name(db, solicitud.requested_role)
    if not role:
        raise HTTPException(status_code=400, detail="Rol solicitado no existe")

    # Crear usuario
    user_repo = UserRepository()
    new_user = user_repo.create(db, User(
        username=data.username,
        email=solicitud.email,
        full_name=solicitud.full_name,
        hashed_password=hash_password(data.password),  # Guardamos la contraseña hasheada
        enabled=True,
        role_id=role.id,
        area=solicitud.area
    ))

    # Enviar las credenciales por correo
    send_credentials_email(
        to_email=solicitud.email,
        username=data.username,
        password=data.password  # Se envía la contraseña en texto plano SOLO por correo
    )

    return {"message": "Usuario creado exitosamente", "user": new_user}




@router_account.get("/", response_model=List[dict])
def get_all_account_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Obtiene todos los registros de la tabla AccountRequest.
    """
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")
    repo = AccountRequestRepository()
    account_requests = repo.get_not_accepted(db)
    if not account_requests:
        raise HTTPException(status_code=404, detail="No se encontraron solicitudes de cuenta.")
    return [
        {
            "id": req.id,
            "full_name": req.full_name or "",
            "email": req.email or "",
            "role": req.requested_role or "",
            "area": req.area or "",
            "motivacion": req.motivo or "",
            "created_at": req.created_at,
            "status": req.status
        }
        for req in account_requests
    ]

 