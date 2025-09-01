from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel import select

from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.domain.VitalSign import VitalSign

def guardar_vital(db: Session, data: dict) -> VitalSign:
    # Buscar paciente por DNI
    paciente = db.exec(select(Paciente).where(Paciente.dni == data["dni"])).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar si ya existe un registro de signos vitales para ese DNI
    vital_existente = db.exec(select(VitalSign).where(VitalSign.dni == data["dni"])).first()

    campos_signos = ["temperatura", "f_card", "f_resp", "talla", "peso"]
    hay_nulos = False
    if vital_existente:
        for campo in campos_signos:
            valor = getattr(vital_existente, campo)
            if valor in [None, 0.0, "", 0]:
                hay_nulos = True
                break

        if hay_nulos:
            # Actualiza solo los campos que vienen en data y están completos
            for campo in campos_signos:
                if campo in data and data[campo] not in [None, 0.0, "", 0]:
                    setattr(vital_existente, campo, data[campo])
            # Calcular y actualizar IMC si peso y talla están presentes y válidos
            peso = getattr(vital_existente, "peso", None)
            talla = getattr(vital_existente, "talla", None)
            if peso and talla and talla > 0:
                vital_existente.imc = peso / talla
            else:
                vital_existente.imc = None
            # Actualizar fecha_registro
            vital_existente.fecha_registro = datetime.now()
            db.commit()
            db.refresh(vital_existente)
            return vital_existente
        else:
            # Todos los campos están completos, permite crear un nuevo registro
            data["paciente_hce"] = paciente.hce
            data["edad"] = paciente.edad
            data["genero"] = paciente.genero
            # Calcular IMC si peso y talla están presentes y válidos
            peso = data.get("peso")
            talla = data.get("talla")
            if peso and talla and talla > 0:
                data["imc"] = peso / talla
            else:
                data["imc"] = None
            # Asignar fecha de registro actual
            data["fecha_registro"] = datetime.now()
            nuevo = VitalSign(**data)
            db.add(nuevo)
            db.commit()
            db.refresh(nuevo)
            return nuevo
    else:
        # Si no existe, crea el registro con datos del paciente
        data["paciente_hce"] = paciente.hce
        data["edad"] = paciente.edad
        data["genero"] = paciente.genero
        # Calcular IMC si peso y talla están presentes y válidos
        peso = data.get("peso")
        talla = data.get("talla")
        if peso and talla and talla > 0:
            data["imc"] = peso / talla
        else:
            data["imc"] = None
        # Asignar fecha de registro actual
        data["fecha_registro"] = datetime.now()
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
        .where(VitalSign.paciente_hce == paciente.hce)
        .order_by(VitalSign.id.desc())
    ).first()

    if not vital:
        raise HTTPException(status_code=404, detail="No hay signos vitales registrados para este paciente")

    return vital


def obtener_vitalsign_por_id(db: Session, id: int) -> VitalSign | None:
    return db.get(VitalSign, id)

def obtener_vitalsigns_por_paciente_hce(db: Session, paciente_hce: str) -> list[VitalSign]:
    return db.exec(select(VitalSign).where(VitalSign.paciente_hce == paciente_hce)).all()

def obtener_vitalsigns_por_dni(db: Session, dni: str) -> list[VitalSign]:
    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return db.exec(select(VitalSign).where(VitalSign.paciente_hce == paciente.hce)).all()

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
    
    registros = db.exec(select(VitalSign).where(VitalSign.paciente_hce == paciente.hce)).all()
    count = len(registros)
    for v in registros:
        db.delete(v)
    db.commit()
    return count
