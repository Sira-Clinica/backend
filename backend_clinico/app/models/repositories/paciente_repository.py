from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel import select, or_
from datetime import datetime


from backend_clinico.app.models.domain.Paciente import Paciente

def generar_hce(db: Session) -> str:
    
    anio_actual = datetime.now().year
    
    prefijo = f"HCE-{anio_actual}-"
    ultimo = db.exec(
        select(Paciente)
        .where(Paciente.hce.like(f"{prefijo}%"))
        .order_by(Paciente.hce.desc())
    ).first()
    if ultimo and ultimo.hce:
        try:
            numero = int(ultimo.hce.split("-")[-1])
        except Exception:
            numero = 0
    else:
        numero = 0
    nuevo_numero = numero + 1
    return f"{prefijo}{nuevo_numero:03d}"


def guardar_paciente(db: Session, data: dict) -> Paciente:
    if "hce" not in data or not data["hce"]:
        data["hce"] = generar_hce(db)
    nuevo = Paciente(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def buscar_pacientes(db: Session, nombre: str = None, apellido: str = None, dni: str = None, hce: str = None):
    query = select(Paciente)
    condiciones = []
    if nombre:
        condiciones.append(Paciente.nombre.ilike(f"%{nombre}%"))
    if apellido:
        condiciones.append(Paciente.apellido.ilike(f"%{apellido}%"))
    if dni:
        condiciones.append(Paciente.dni == dni)
    if hce:
        condiciones.append(Paciente.hce == hce)
    if condiciones:
        query = query.where(or_(*condiciones))
    return db.exec(query).all()

def obtener_pacientes(db: Session) -> list[Paciente]:
    return db.exec(select(Paciente)).all()


def obtener_paciente_por_id(db: Session, paciente_hce: str) -> Paciente | None:
    return db.get(Paciente, paciente_hce)


def obtener_paciente_por_dni(db: Session, dni: str) -> Paciente | None:
    return db.exec(select(Paciente).where(Paciente.dni == dni)).first()


def actualizar_paciente(db: Session, paciente_hce: str, nuevos_datos: dict) -> Paciente | None:
    paciente = obtener_paciente_por_id(db, paciente_hce)
    if paciente:
        for clave, valor in nuevos_datos.items():
            setattr(paciente, clave, valor)
        db.commit()
        db.refresh(paciente)
    return paciente


def actualizar_paciente_por_dni(db: Session, dni: str, nuevos_datos: dict) -> Paciente | None:
    paciente = obtener_paciente_por_dni(db, dni)
    if paciente:
        for clave, valor in nuevos_datos.items():
            setattr(paciente, clave, valor)
        db.commit()
        db.refresh(paciente)
    return paciente


def eliminar_paciente(db: Session, paciente_hce: str) -> Paciente | None:
    paciente = obtener_paciente_por_id(db, paciente_hce)
    if paciente:
        db.delete(paciente)
        db.commit()
    return paciente


def eliminar_paciente_por_dni(db: Session, dni: str) -> Paciente | None:
    paciente = obtener_paciente_por_dni(db, dni)
    if paciente:
        db.delete(paciente)
        db.commit()
    return paciente