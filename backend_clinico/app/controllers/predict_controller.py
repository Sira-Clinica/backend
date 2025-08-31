from fastapi import APIRouter, Depends, HTTPException

from sqlmodel import Session,select

from backend_clinico.app.Dtos.DiagnosticoInput import DiagnosticoInput
from backend_clinico.app.Dtos.DiagnosticoSimpleInput import DiagnosticoSimpleInput
from backend_clinico.app.Dtos.VitalSignInput import VitalSignInput
from backend_clinico.app.models.domain.Diagnostico import Diagnostico
from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.domain.VitalSign import VitalSign
from backend_clinico.app.models.repositories.historialclinico_repository import guardar_en_historial_clinico
from backend_clinico.app.models.repositories.vitalsign_repository import obtener_ultimo_vitalsign_por_dni
from backend_clinico.app.services.prediccion_service import predecir_diagnostico
from backend_clinico.app.models.repositories.diagnostico_repository import (
    guardar_diagnostico,
    guardar_diagnostico_con_vitalsign,
    obtener_diagnosticos,
    obtener_diagnostico_por_id,
    eliminar_diagnostico,
    actualizar_diagnostico,
    obtener_diagnosticos_por_dni,
    actualizar_ultimo_diagnostico_por_dni,
    eliminar_diagnosticos_por_dni,
    obtener_ultimo_diagnostico_por_dni
)
from backend_clinico.app.models.conection.dependency import get_db
from backend_clinico.security.infrastructure.auth_dependencies import get_current_user
from backend_clinico.security.domain.model.user import User

predict_router = APIRouter(prefix="/predict", tags=["Diagnóstico"])


def verificar_permisos(current_user: User):
    if current_user.role_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")


@predict_router.post("/", summary="Realizar predicción clínica")
def hacer_prediccion(
    data: DiagnosticoInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    resultado = predecir_diagnostico(**data.dict())
    guardar_diagnostico(db, {**data.dict(), "resultado": resultado})
    return {"diagnostico": resultado}


@predict_router.get("/", summary="Listar diagnósticos")
def listar_diagnosticos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    return obtener_diagnosticos(db)


@predict_router.get("/{diagnostico_id}", summary="Obtener diagnóstico por ID")
def obtener_por_id(
    diagnostico_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    diag = obtener_diagnostico_por_id(db, diagnostico_id)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")
    return diag


@predict_router.delete("/{diagnostico_id}", summary="Eliminar diagnóstico")
def eliminar(
    diagnostico_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    diag = eliminar_diagnostico(db, diagnostico_id)
    if not diag:
        raise HTTPException(status_code=404, detail="No encontrado")
    return {"message": "Eliminado correctamente"}


@predict_router.put("/{diagnostico_id}", summary="Actualizar diagnóstico")
def actualizar(
    diagnostico_id: int,
    input: DiagnosticoInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    nuevos_datos = input.dict()
    diag_actualizado = actualizar_diagnostico(db, diagnostico_id, nuevos_datos)
    if not diag_actualizado:
        raise HTTPException(status_code=404, detail="No encontrado")
    return diag_actualizado

@predict_router.post("/from-dni/{dni}", summary="Realizar predicción clínica usando DNI del paciente")
def predecir_con_dni(
    dni: str,
    data: DiagnosticoSimpleInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

    vital = obtener_ultimo_vitalsign_por_dni(db, dni)

    resultado = predecir_diagnostico(
        temperatura=vital.temperatura,
        edad=vital.edad,
        f_card=vital.f_card,
        f_resp=vital.f_resp,
        talla=vital.talla,
        peso=vital.peso,
        genero=vital.genero,
        motivo_consulta=data.motivo_consulta,
        examenfisico=data.examenfisico
    )

    diagnostico = Diagnostico(
        temperatura=vital.temperatura,
        edad=vital.edad,
        f_card=vital.f_card,
        f_resp=vital.f_resp,
        talla=vital.talla,
        peso=vital.peso,
        genero=vital.genero,
        motivo_consulta=data.motivo_consulta,
        examenfisico=data.examenfisico,
        resultado=resultado,
        dni=dni,
        indicaciones=data.indicaciones,
        medicamentos=data.medicamentos,
        notas=data.notas,
        imc=vital.imc
    )

    db.add(diagnostico)

    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    guardar_en_historial_clinico(db, diagnostico, paciente)
    db.commit()
    db.refresh(diagnostico)

    return {"diagnostico": resultado, "datos": diagnostico}



@predict_router.get("/by-dni/{dni}", summary="Obtener diagnósticos por DNI")
def obtener_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    resultados = obtener_diagnosticos_por_dni(db, dni)
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron diagnósticos para este DNI")
    return resultados

@predict_router.put("/by-dni/{dni}", summary="Actualizar último diagnóstico por DNI")
def actualizar_por_dni(
    dni: str,
    data: DiagnosticoSimpleInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    actualizado = actualizar_ultimo_diagnostico_por_dni(db, dni, {
        "motivo_consulta": data.motivo_consulta,
        "examenfisico": data.examenfisico
    })
    if not actualizado:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado para este DNI")
    return actualizado

@predict_router.delete("/by-dni/{dni}", summary="Eliminar todos los diagnósticos por DNI")
def eliminar_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    verificar_permisos(current_user)
    eliminados = eliminar_diagnosticos_por_dni(db, dni)
    if not eliminados:
        raise HTTPException(status_code=404, detail="No se encontraron diagnósticos para eliminar")
    return {"message": f"Se eliminaron {eliminados} diagnósticos para el DNI {dni}"}


@predict_router.get("/ultimo/{dni}", summary="Obtener último diagnóstico por DNI")
def get_ultimo_diagnostico_por_dni(
    dni: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Diagnostico:
    if current_user.role_id not in [1, 2]:
        raise HTTPException(status_code=403, detail="No autorizado")

    diagnostico = obtener_ultimo_diagnostico_por_dni(db, dni)

    if not diagnostico:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")

    return diagnostico
