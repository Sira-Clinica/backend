
from fastapi import HTTPException
from sqlmodel import Session
from sqlmodel import select


from backend_clinico.app.models.domain.Paciente import Paciente

def guardar_paciente(db: Session, data: dict) -> Paciente:
    nuevo = Paciente(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


def obtener_pacientes(db: Session) -> list[Paciente]:
    return db.exec(select(Paciente)).all()


def obtener_paciente_por_id(db: Session, paciente_id: int) -> Paciente | None:
    return db.get(Paciente, paciente_id)


def obtener_paciente_por_dni(db: Session, dni: str) -> Paciente | None:
    return db.exec(select(Paciente).where(Paciente.dni == dni)).first()


def actualizar_paciente(db: Session, paciente_id: int, nuevos_datos: dict) -> Paciente | None:
    paciente = obtener_paciente_por_id(db, paciente_id)
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


def eliminar_paciente(db: Session, paciente_id: int) -> Paciente | None:
    paciente = obtener_paciente_por_id(db, paciente_id)
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