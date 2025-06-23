from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend_clinico.app.Dtos.PacienteInput import PacienteInput
from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.app.models.repositories.paciente_repository import (
    guardar_paciente,
    obtener_pacientes,
    obtener_paciente_por_id,
    obtener_paciente_por_dni,
    actualizar_paciente,
    actualizar_paciente_por_dni,
    eliminar_paciente,
    eliminar_paciente_por_dni,
)
from backend_clinico.security.domain.model.user import User
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user


paciente_router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


def verificar_permisos(current_user: User):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")


@paciente_router.post("/", summary="Registrar paciente")
def registrar_paciente(
    data: PacienteInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

    nuevo = guardar_paciente(db, data.dict())
    return {"message": "Paciente registrado correctamente", "paciente": nuevo}


@paciente_router.get("/", summary="Listar todos los pacientes")
def listar_pacientes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    return obtener_pacientes(db)


@paciente_router.get("/{paciente_id}", summary="Obtener paciente por ID")
def obtener_por_id(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    paciente = obtener_paciente_por_id(db, paciente_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


@paciente_router.get("/by-dni/{dni}", summary="Obtener paciente por DNI")
def obtener_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    paciente = obtener_paciente_por_dni(db, dni)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


@paciente_router.put("/{paciente_id}", summary="Actualizar paciente por ID")
def actualizar_por_id(
    paciente_id: int,
    data: PacienteInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    actualizado = actualizar_paciente(db, paciente_id, data.dict())
    if not actualizado:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return actualizado


@paciente_router.put("/by-dni/{dni}", summary="Actualizar paciente por DNI")
def actualizar_por_dni(
    dni: str,
    data: PacienteInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    actualizado = actualizar_paciente_por_dni(db, dni, data.dict())
    if not actualizado:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return actualizado


@paciente_router.delete("/{paciente_id}", summary="Eliminar paciente por ID")
def eliminar_por_id(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    eliminado = eliminar_paciente(db, paciente_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"message": "Paciente eliminado correctamente"}


@paciente_router.delete("/by-dni/{dni}", summary="Eliminar paciente por DNI")
def eliminar_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    eliminado = eliminar_paciente_por_dni(db, dni)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"message": f"Paciente con DNI {dni} eliminado correctamente"}
