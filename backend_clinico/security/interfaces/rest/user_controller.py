from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from backend_clinico.security.application.UserService import UserService
from backend_clinico.security.infrastructure.auth_dependencies import get_db, get_current_user
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.domain.repository.user_repository import UserRepository,  send_password_change_email
from backend_clinico.security.resource.request.user_request import UserPasswordChangeRequest, UserUpdateRequest
from backend_clinico.security.resource.response.user_response import MedicoResponse

router_user = APIRouter(prefix="/users", tags=["Usuarios"])

def verificar_permisos(current_user: User):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

@router_user.get("/", summary="Listar todos los usuarios", response_model=List[User])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    user_service = UserService(UserRepository())
    return user_service.get_all_users(db)


@router_user.get(
    "/medicos",
    summary="Listar nombres completos de los médicos",
    response_model=List[MedicoResponse]
)
def listar_medicos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

    user_service = UserService(UserRepository())
    return user_service.get_all_medicos(db)


@router_user.get("/{user_id}", summary="Obtener usuario por ID", response_model=User)
def obtener_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    user_service = UserService(UserRepository())
    try:
        return user_service.get_user_by_id(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    



@router_user.delete("/{user_id}", summary="Eliminar usuario por ID")
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="No autorizado")

    user_service = UserService(UserRepository())
    try:
        return user_service.delete_user(db, user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router_user.put("/{user_id}", summary="Actualizar datos del usuario")
def actualizar_usuario(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 1 and current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="No autorizado")

    user_service = UserService(UserRepository())
    try:
        return user_service.update_user(db, user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router_user.put("/{user_id}/change-password", summary="Cambiar contraseña del usuario")
def cambiar_contraseña(
    user_id: int,
    data: UserPasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)

    user_service = UserService(UserRepository())
    
    try:
        # Primero obtenemos los datos del usuario antes del cambio
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Cambiamos la contraseña
        updated_user = user_service.change_password(db, user_id, data.old_password, data.new_password)
        
        # Enviamos el correo específico para cambio de contraseña
        send_password_change_email(
            to_email=user.email,
            username=user.username,
            new_password=data.new_password
        )
        
        return {
            "message": "Contraseña actualizada correctamente y correo de notificación enviado", 
            "user": updated_user
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar solicitud: {str(e)}")