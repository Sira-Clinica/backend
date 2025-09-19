from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend_clinico.app.Dtos.ConsultaInput import ConsultaInput, UpdateStatusConsultaInput
from backend_clinico.app.models.domain.Consultas import Consultas
from backend_clinico.app.models.repositories.consulta_repositori import (
   actualizar_status_consulta,
    actualizar_consulta,  
    guardar_consulta,
    obtener_consultas_hoy,
    obtener_consultas_medico,
    obtener_consultas_por_paciente,
    obtener_consultas_por_medico,
    obtener_total_consultas_medico,
    obtener_total_consultas_ultimos_7_dias,
    get_status_por_id_consulta,
    finalizar_consulta  
)
from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user
from backend_clinico.security.domain.model.user import User

consulta_router = APIRouter(prefix="/consultas", tags=["Consultas"])

def verificar_permisos(current_user: User):
    if current_user.role_id not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

@consulta_router.post("/", summary="Registrar consulta (admin y enfermero)")
def registrar_consulta(
    data: ConsultaInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1,3]:
        raise HTTPException(status_code=403, detail="No autorizado")

    consulta = guardar_consulta(db, data.dni, data.user_fullname_medic, data.dia, data.hora, data.minuto)
    return {"message": "Consulta registrada correctamente", "consulta": consulta}

@consulta_router.get("/paciente/{dni}", summary="Obtener consultas por paciente (admin y enfermero)")
def listar_consultas_paciente(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")
    return obtener_consultas_por_paciente(db, dni)

@consulta_router.get("/medico/{user_fullname_medic}", summary="Obtener consultas por médico (admin y enfermero)")
def listar_consultas_medico(
    user_fullname_medic: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")
    return obtener_consultas_por_medico(db, user_fullname_medic)

@consulta_router.put("/{id_consulta}", summary="Actualizar consulta por id (admin, enfermero y medico)")
def actualizar_consulta_id(
        id_consulta: int,
        data: ConsultaInput,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role_id not in [1, 2, 3]:
            raise HTTPException(status_code=403, detail="No autorizado")
        # Convertir los datos a dict, excluyendo valores None si es necesario
        datos_actualizacion = {k: v for k, v in data.dict().items() if v is not None}
        
        consulta = actualizar_consulta(db, id_consulta, datos_actualizacion)
        
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        
        return {"message": "Consulta actualizada correctamente", "consulta": consulta}


@consulta_router.patch("/{consulta_dni}/status", summary="Actualizar solo el status de una consulta (admin y enfermero)")
def actualizar_status(
    consulta_dni: str,
    data: UpdateStatusConsultaInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")
    consulta = actualizar_status_consulta(db, consulta_dni, data.status)
    return {"message": "Status actualizado correctamente", "consulta": consulta}


@consulta_router.get("/hoy", response_model=List[Consultas], summary="Obtener consultas del día de hoy (admin y enfermero)")
def listar_consultas_hoy(
    paciente: Optional[str] = Query(None, description="Nombre o apellido del paciente"),
    hce: Optional[str] = Query(None, description="HCE del paciente"),
    dni: Optional[str] = Query(None, description="DNI del paciente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista las consultas programadas para el día actual.
    Se puede filtrar opcionalmente por nombre/apellido del paciente, HCE o DNI.
    """
    if current_user.role_id not in [1, 3]:
        raise HTTPException(status_code=403, detail="No autorizado")

    consultas = obtener_consultas_hoy(db, paciente, hce, dni)
    return consultas


@consulta_router.get("/hoy/medico", response_model=List[Consultas], summary="Obtener consultas de hoy para el médico autenticado")
def listar_consultas_medico(
    paciente: Optional[str] = Query(None, description="Nombre o apellido del paciente"),
    hce: Optional[str] = Query(None, description="HCE del paciente"),
    dni: Optional[str] = Query(None, description="DNI del paciente"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista las consultas del día actual asociadas al médico autenticado.
    Solo accesible si el usuario tiene rol de médico.
    """
    if current_user.role_id != 2: 
        raise HTTPException(status_code=403, detail="Solo los médicos pueden acceder a este recurso.")

    consultas = obtener_consultas_medico(
        db=db,
        medico_fullname=current_user.full_name,
        paciente=paciente,
        hce=hce,
        dni=dni
    )
    return consultas



@consulta_router.get("/total/medico", summary="Cantidad total de consultas para el médico autenticado")
def total_consultas_medico(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="Solo los médicos pueden acceder a este recurso.")
    
    total = obtener_total_consultas_medico(db, current_user.full_name)
    return {"total_consultas": total}


@consulta_router.get("/total/medico/ultimos7dias", summary="Cantidad de consultas en los últimos 7 días para el médico autenticado")
def total_consultas_ultimos_7_dias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="Solo los médicos pueden acceder a este recurso.")

    total = obtener_total_consultas_ultimos_7_dias(db, current_user.full_name)
    return {"total_consultas_ultimos_7_dias": total}



@consulta_router.get("/status/{id_consulta}", summary="Obtener status de la consulta por ID (admin , enfermero y médico)")
def status_consulta_por_id(
    id_consulta: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id not in [1, 3,2]:
        raise HTTPException(status_code=403, detail="No autorizado")

    status = get_status_por_id_consulta(db, id_consulta)
    return {"id_consulta": id_consulta, "status": status}



@consulta_router.patch("/{consulta_id}/finalizar", summary="Finalizar consulta (solo médicos)")
def finalizar_consulta_endpoint(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="Solo los médicos pueden finalizar consultas.")
    
    consulta = finalizar_consulta(db, consulta_id)
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    
    return {"message": "Consulta finalizada correctamente", "consulta": consulta}