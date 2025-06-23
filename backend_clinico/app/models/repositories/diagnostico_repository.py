

from sqlmodel import Session, select
from backend_clinico.app.models.domain.Diagnostico import Diagnostico
from backend_clinico.app.models.domain.VitalSign import VitalSign


def guardar_diagnostico(db: Session, data: dict) -> Diagnostico:
    nuevo = Diagnostico(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def obtener_diagnosticos(db: Session) -> list[Diagnostico]:
    return db.exec(select(Diagnostico)).all()

def obtener_diagnostico_por_id(db: Session, diagnostico_id: int) -> Diagnostico | None:
    return db.get(Diagnostico, diagnostico_id)

def eliminar_diagnostico(db: Session, diagnostico_id: int) -> Diagnostico | None:
    diag = obtener_diagnostico_por_id(db, diagnostico_id)
    if diag:
        db.delete(diag)
        db.commit()
    return diag

def actualizar_diagnostico(db: Session, diagnostico_id: int, nuevos_datos: dict) -> Diagnostico | None:
    diag = obtener_diagnostico_por_id(db, diagnostico_id)
    if diag:
        for clave, valor in nuevos_datos.items():
            setattr(diag, clave, valor)
        db.commit()
        db.refresh(diag)
    return diag


def guardar_diagnostico_con_vitalsign(
    db: Session, motivo_consulta: str, examenfisico: str, resultado: str
) -> Diagnostico:
    # Obtener último registro de signos vitales
    vital = db.exec(select(VitalSign).order_by(VitalSign.id.desc())).first()
    if not vital:
        raise ValueError("No se encontraron signos vitales registrados.")

    nuevo_diag = Diagnostico(
        temperatura=vital.temperatura,
        edad=vital.edad,
        f_card=vital.f_card,
        f_resp=vital.f_resp,
        talla=vital.talla,
        peso=vital.peso,
        genero=vital.genero,
        motivo_consulta=motivo_consulta,
        examenfisico=examenfisico,
        resultado=resultado
    )

    db.add(nuevo_diag)
    db.commit()
    db.refresh(nuevo_diag)
    return nuevo_diag


def obtener_diagnosticos_por_dni(db: Session, dni: str) -> list[Diagnostico]:
    return db.exec(select(Diagnostico).where(Diagnostico.dni == dni)).all()

def actualizar_ultimo_diagnostico_por_dni(db: Session, dni: str, nuevos_datos: dict) -> Diagnostico | None:
    diagnostico = db.exec(
        select(Diagnostico).where(Diagnostico.dni == dni).order_by(Diagnostico.id.desc())
    ).first()
    if diagnostico:
        for clave, valor in nuevos_datos.items():
            setattr(diagnostico, clave, valor)
        db.commit()
        db.refresh(diagnostico)
    return diagnostico

def eliminar_diagnosticos_por_dni(db: Session, dni: str) -> int:
    diagnosticos = db.exec(select(Diagnostico).where(Diagnostico.dni == dni)).all()
    count = 0
    for diag in diagnosticos:
        db.delete(diag)
        count += 1
    db.commit()
    return count


def obtener_ultimo_diagnostico_por_dni(db, dni: str) -> Diagnostico | None:
    return db.exec(
        select(Diagnostico)
        .where(Diagnostico.dni == dni)
        .order_by(Diagnostico.id.desc()) 
    ).first()