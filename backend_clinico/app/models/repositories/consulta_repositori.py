from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException
from sqlmodel import Session, and_, or_, select
from sqlalchemy import func

from backend_clinico.app.models.domain.Paciente import Paciente

from backend_clinico.app.models.domain.Consultas import Consultas
from backend_clinico.security.domain.model.user import User

from sqlalchemy import and_, func
from datetime import datetime

def guardar_consulta(db: Session, status: str, dni: str, user_fullname: str, dia: int, hora: int, minuto: int) -> Consultas:
    # Buscar paciente por DNI
    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar usuario médico por nombre completo y rol
    medico = db.exec(
        select(User).where(
            User.full_name == user_fullname,
            User.role_id == 2
        )
    ).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado o no es médico")

    anio_actual = datetime.now().year
    mes_actual = datetime.now().month

    # Validar que la fecha no sea pasada
    fecha_consulta = datetime(anio_actual, mes_actual, dia, hora, minuto)
    if fecha_consulta < datetime.now():
        raise HTTPException(status_code=400, detail="No se puede registrar una consulta en una fecha/hora pasada.")

    # Validar si el médico ya tiene una consulta en ese horario
    consulta_existente = db.exec(
        select(Consultas).where(
            and_(
                Consultas.anio == anio_actual,
                Consultas.mes == mes_actual,
                Consultas.dia == dia,
                Consultas.hora == hora,
                Consultas.minuto == minuto,
                Consultas.user_fullname == medico.full_name
            )
        )
    ).first()

    if consulta_existente:
        raise HTTPException(status_code=400, detail="Este horario ya está ocupado para este médico.")

    # Crear la nueva consulta
    nueva_consulta = Consultas(
        paciente_hce=paciente.hce,
        paciente_nombre=paciente.nombre,
        paciente_apelido=paciente.apellido,
        dni=paciente.dni,
        status=status,
        anio=anio_actual,
        mes=mes_actual,
        dia=dia,
        hora=hora,
        minuto=minuto,
        user_fullname=medico.full_name
    )
    db.add(nueva_consulta)
    db.commit()
    db.refresh(nueva_consulta)
    return nueva_consulta



def obtener_consultas_por_paciente(db: Session, dni: str):
    return db.exec(select(Consultas).where(Consultas.dni == dni)).all()

def obtener_consultas_por_medico(db: Session, user_fullname: str):
    return db.exec(select(Consultas).where(Consultas.user_fullname == user_fullname)).all()



def actualizar_status_consulta(db: Session, dni: str, status: str) -> Consultas:
    consulta = db.exec(
           select(Consultas).where(Consultas.dni == dni).order_by(Consultas.fecha.desc())
    ).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    consulta.status = status
    db.commit()
    db.refresh(consulta)
    return consulta



def obtener_consultas_hoy(
    db: Session,
    paciente: Optional[str] = None,
    hce: Optional[str] = None,
    dni: Optional[str] = None
) -> List[Consultas]:
    """Obtiene las consultas del día actual con filtros opcionales por paciente, HCE o DNI."""
    hoy = datetime.now()
    query = select(Consultas).where(
        (Consultas.anio == hoy.year) &
        (Consultas.mes == hoy.month) &
        (Consultas.dia == hoy.day)
    )

    # Aplicar filtros opcionales
    if paciente:
        query = query.where(
            or_(
                Consultas.paciente_nombre.ilike(f"%{paciente}%"),
                Consultas.paciente_apelido.ilike(f"%{paciente}%")
            )
        )
    if hce:
        query = query.where(Consultas.paciente_hce == hce)
    if dni:
        query = query.where(Consultas.dni == dni)

    return db.exec(query).all()


def obtener_consultas_medico(
    db: Session,
    medico_fullname: str,
    paciente: Optional[str] = None,
    hce: Optional[str] = None,
    dni: Optional[str] = None
) -> List[Consultas]:
    """Obtiene las consultas del día actual solo para un médico específico."""
    hoy = datetime.now()
    query = select(Consultas).where(
        (Consultas.anio == hoy.year) &
        (Consultas.mes == hoy.month) &
        (Consultas.dia == hoy.day) &
        (Consultas.user_fullname == medico_fullname)
    )

    if paciente:
        query = query.where(
            or_(
                Consultas.paciente_nombre.ilike(f"%{paciente}%"),
                Consultas.paciente_apelido.ilike(f"%{paciente}%")
            )
        )
    if hce:
        query = query.where(Consultas.paciente_hce == hce)
    if dni:
        query = query.where(Consultas.dni == dni)

    return db.exec(query).all()


def obtener_total_consultas_medico(
    db: Session,
    medico_fullname: str
) -> int:
    """
    Retorna la cantidad total de consultas para un médico específico.
    """
    query = select(func.count()).select_from(Consultas).where(
        Consultas.user_fullname == medico_fullname
    )
    result = db.exec(query).one()
    return result or 0




def obtener_total_consultas_ultimos_7_dias(
    db: Session,
    medico_fullname: str
) -> int:
    """
    Retorna la cantidad de consultas en los últimos 7 días para un médico específico.
    """
    hoy = datetime.now()
    hace_siete_dias = hoy - timedelta(days=7)

    # Suponiendo que tu modelo usa anio, mes, dia en lugar de un campo datetime completo
    query = select(func.count()).select_from(Consultas).where(
        (Consultas.user_fullname == medico_fullname) &
        (
            (Consultas.anio > hace_siete_dias.year) |
            (
                (Consultas.anio == hace_siete_dias.year) &
                (
                    (Consultas.mes > hace_siete_dias.month) |
                    (
                        (Consultas.mes == hace_siete_dias.month) &
                        (Consultas.dia >= hace_siete_dias.day)
                    )
                )
            )
        )
    )

    result = db.exec(query).one()
    return result or 0