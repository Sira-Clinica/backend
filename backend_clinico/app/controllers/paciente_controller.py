from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend_clinico.app.Dtos.PacienteInput import PacienteInput
from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.app.models.repositories.vitalsign_repository import guardar_vital
from backend_clinico.app.models.repositories.paciente_repository import (
    buscar_pacientes,
    generar_hce,
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
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

@paciente_router.post("/", summary="Registrar paciente")
def registrar_paciente(
    data: PacienteInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")
    hce_unico = generar_hce(db)

    # Convertir el DTO a diccionario y añadir el HCE
    paciente_data = data.dict()
    paciente_data["hce"] = hce_unico

    nuevo = guardar_paciente(db, data.dict())

    # Crear registro de signos vitales con datos por defecto
    vital_data = {
        "paciente_hce": nuevo.hce,
        "dni": nuevo.dni,
        "edad": nuevo.edad,
        "genero": nuevo.genero,
        # Puedes poner valores por defecto o None para los demás campos
        "temperatura": 0.0,
        "f_card": None,
        "f_resp": None,
        "talla": None,
        "peso": None,
    }
    guardar_vital(db, vital_data)

    return {"message": "Paciente registrado correctamente", "paciente": nuevo}

@paciente_router.get("/", summary="Listar todos los pacientes")
def listar_pacientes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    return obtener_pacientes(db)


@paciente_router.get("/buscar", summary="Buscar pacientes por nombre, apellido, DNI o HCE")
def buscar_pacientes_endpoint(
    nombre: str = None,
    apellido: str = None,
    dni: str = None,
    hce: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    resultados = buscar_pacientes(db, nombre, apellido, dni, hce)
    return resultados

@paciente_router.get("/{paciente_hce}", summary="Obtener paciente por HCE")
def obtener_por_hce(
    paciente_hce: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    paciente = obtener_paciente_por_id(db, paciente_hce)
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

@paciente_router.put("/{paciente_hce}", summary="Actualizar paciente por HCE")
def actualizar_por_hce(
    paciente_hce: str,
    data: PacienteInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    actualizado = actualizar_paciente(db, paciente_hce, data.dict())
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

@paciente_router.delete("/{paciente_hce}", summary="Eliminar paciente por HCE")
def eliminar_por_hce(
    paciente_hce: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    eliminado = eliminar_paciente(db, paciente_hce)
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

