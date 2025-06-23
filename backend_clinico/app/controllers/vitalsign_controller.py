from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend_clinico.app.Dtos.VitalSignInput import VitalSignInput
from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.domain.VitalSign import VitalSign

from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.app.models.repositories.vitalsign_repository import (
    guardar_vital,
    obtener_vitalsign_por_id,
    obtener_vitalsigns_por_paciente_id,
    obtener_vitalsigns_por_dni,
    obtener_ultimo_vitalsign_por_dni,
    actualizar_vitalsign,
    eliminar_vitalsign,
    eliminar_vitalsigns_por_dni,
)
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user
from backend_clinico.security.domain.model.user import User


vitalsign_router = APIRouter(prefix="/vitalsign", tags=["Signos Vitales"])
def verificar_permisos(current_user: User):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")


@vitalsign_router.post("/", summary="Registrar signos vitales")
def registrar_vitalsign(
    data: VitalSignInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

    paciente = db.exec(select(Paciente).where(Paciente.dni == data.dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    vital_data = data.dict()
    vital_data["paciente_id"] = paciente.id

    nuevo_vital = guardar_vital(db, vital_data)
    return {
        "message": "Signos vitales registrados correctamente",
        "vitalsign": nuevo_vital
    }


@vitalsign_router.get("/{id}", summary="Obtener signo vital por ID")
def obtener_por_id(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verificar_permisos(current_user)
    vital = obtener_vitalsign_por_id(db, id)
    if not vital:
        raise HTTPException(status_code=404, detail="No encontrado")
    return vital


@vitalsign_router.get("/dni/{dni}", summary="Obtener signos vitales por DNI")
def obtener_por_dni(dni: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verificar_permisos(current_user)
    return obtener_vitalsigns_por_dni(db, dni)


@vitalsign_router.get("/ultimo/{dni}", summary="Obtener último signo vital por DNI")
def obtener_ultimo(dni: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verificar_permisos(current_user)
    return obtener_ultimo_vitalsign_por_dni(db, dni)


@vitalsign_router.put("/{id}", summary="Actualizar signo vital por ID")
def actualizar(id: int, data: VitalSignInput, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verificar_permisos(current_user)
    actualizado = actualizar_vitalsign(db, id, data.dict())
    if not actualizado:
        raise HTTPException(status_code=404, detail="No encontrado")
    return actualizado


@vitalsign_router.delete("/{id}", summary="Eliminar signo vital por ID")
def eliminar(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verificar_permisos(current_user)
    eliminado = eliminar_vitalsign(db, id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="No encontrado")
    return {"message": f"Signo vital con ID {id} eliminado correctamente"}


@vitalsign_router.delete("/dni/{dni}", summary="Eliminar todos los signos vitales por DNI")
def eliminar_por_dni(dni: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    verificar_permisos(current_user)
    eliminados = eliminar_vitalsigns_por_dni(db, dni)
    return {"message": f"{eliminados} signos vitales eliminados para el DNI {dni}"}


@vitalsign_router.get("/by-paciente/{paciente_id}", summary="Obtener signos vitales por ID de paciente")
def obtener_vitals_por_paciente_id(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

    registros = obtener_vitalsigns_por_paciente_id(db, paciente_id)
    if not registros:
        raise HTTPException(status_code=404, detail="No se encontraron signos vitales para este paciente")

    return registros
