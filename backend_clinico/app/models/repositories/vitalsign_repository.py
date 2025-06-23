

from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel import select

from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.domain.VitalSign import VitalSign


def guardar_vital(db: Session, data: dict) -> VitalSign:
    nuevo = VitalSign(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def obtener_ultimo_vitalsign_por_dni(db: Session, dni: str) -> VitalSign:

    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    vital = db.exec(
        select(VitalSign)
        .where(VitalSign.paciente_id == paciente.id)
        .order_by(VitalSign.id.desc())
    ).first()

    if not vital:
        raise HTTPException(status_code=404, detail="No hay signos vitales registrados para este paciente")

    return vital


def obtener_vitalsign_por_id(db: Session, id: int) -> VitalSign | None:
    return db.get(VitalSign, id)

def obtener_vitalsigns_por_paciente_id(db: Session, paciente_id: int) -> list[VitalSign]:
    return db.exec(select(VitalSign).where(VitalSign.paciente_id == paciente_id)).all()

def obtener_vitalsigns_por_dni(db: Session, dni: str) -> list[VitalSign]:
    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return db.exec(select(VitalSign).where(VitalSign.paciente_id == paciente.id)).all()

def actualizar_vitalsign(db: Session, id: int, nuevos_datos: dict) -> VitalSign | None:
    vital = obtener_vitalsign_por_id(db, id)
    if vital:
        for clave, valor in nuevos_datos.items():
            setattr(vital, clave, valor)
        db.commit()
        db.refresh(vital)
    return vital


def eliminar_vitalsign(db: Session, id: int) -> VitalSign | None:
    vital = obtener_vitalsign_por_id(db, id)
    if vital:
        db.delete(vital)
        db.commit()
    return vital


def eliminar_vitalsigns_por_dni(db: Session, dni: str) -> int:
    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    registros = db.exec(select(VitalSign).where(VitalSign.paciente_id == paciente.id)).all()
    count = len(registros)
    for v in registros:
        db.delete(v)
    db.commit()
    return count
