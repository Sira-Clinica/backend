from datetime import datetime, timedelta, timezone
from typing import List, Optional
import pytz
from fastapi import HTTPException
from sqlmodel import Session, and_, or_, select
from sqlalchemy import func

from backend_clinico.app.models.domain.Paciente import Paciente
from backend_clinico.app.models.domain.Consultas import Consultas
from backend_clinico.security.domain.model.user import User

from sqlalchemy import and_, func
from datetime import datetime

# Zona horaria de Perú
PERU_TZ = pytz.timezone('America/Lima')

def obtener_fecha_utc() -> datetime:
    """Siempre usar UTC para guardar en DB"""
    return datetime.now(timezone.utc)

def obtener_fecha_peru() -> datetime:
    """Obtiene la fecha y hora actual de Perú"""
    return datetime.now(timezone.utc).astimezone(PERU_TZ)

def guardar_consulta(db: Session, dni: str, user_fullname_medic: str, dia: int, hora: int, minuto: int) -> Consultas:
    # Buscar paciente por DNI
    paciente = db.exec(select(Paciente).where(Paciente.dni == dni)).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar usuario médico por nombre completo y rol
    medico = db.exec(
        select(User).where(
            User.full_name == user_fullname_medic,
            User.role_id == 2
        )
    ).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico no encontrado o no es médico")

    ahora_peru = obtener_fecha_peru()
    anio_actual = ahora_peru.year
    mes_actual = ahora_peru.month

    # Validar que la fecha no sea pasada
    fecha_consulta_peru = PERU_TZ.localize(datetime(anio_actual, mes_actual, dia, hora, minuto))
    fecha_consulta_utc = fecha_consulta_peru.astimezone(timezone.utc)
    if fecha_consulta_peru < ahora_peru:
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
                Consultas.user_fullname_medic == medico.full_name
            )
        )
    ).first()

    if consulta_existente:
        raise HTTPException(status_code=400, detail="Este horario ya está ocupado para este médico.")

    # Crear la nueva consulta
    nueva_consulta = Consultas(
        paciente_hce=paciente.hce,
        paciente_nombre=paciente.nombre,
        paciente_apellido=paciente.apellido,
        dni=paciente.dni,
        status="En espera",
        anio=anio_actual,
        mes=mes_actual,
        dia=dia,
        hora=hora,
        minuto=minuto,
        user_fullname_medic=medico.full_name
    )
    db.add(nueva_consulta)
    db.commit()
    db.refresh(nueva_consulta)
    return nueva_consulta


def obtener_consultas_por_paciente(db: Session, dni: str):
    return db.exec(select(Consultas).where(Consultas.dni == dni)).all()

def obtener_consultas_por_medico(db: Session, user_fullname: str):
    return db.exec(select(Consultas).where(Consultas.user_fullname_medic == user_fullname)).all()

def obtener_consulta_por_id(db: Session, id: int) -> Consultas | None:
    return db.get(Consultas, id)

def actualizar_edit_status_consulta(db: Session, consulta_id: int, edit_status: bool) -> Consultas:
    consulta = db.get(Consultas, consulta_id)
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    
    consulta.edit_status = edit_status
    db.commit()
    db.refresh(consulta)
    return consulta



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

def actualizar_consulta(db: Session, consulta_id: int, nuevos_datos: dict) -> Consultas | None:
    consulta = obtener_consulta_por_id(db, consulta_id)
    if not consulta:
        return None
    
    # Si se está actualizando el DNI, validar que el nuevo DNI existe en pacientes
    if 'dni' in nuevos_datos and nuevos_datos['dni'] != consulta.dni:
        nuevo_dni = nuevos_datos['dni']
        
        # Buscar el paciente con el nuevo DNI
        nuevo_paciente = db.exec(select(Paciente).where(Paciente.dni == nuevo_dni)).first()
        
        if not nuevo_paciente:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró un paciente con DNI: {nuevo_dni}"
            )
        
        # Actualizar los datos del paciente en la consulta automáticamente
        nuevos_datos.update({
            'dni': nuevo_paciente.dni,
            'paciente_nombre': nuevo_paciente.nombre,
            'paciente_apellido': nuevo_paciente.apellido,
            'paciente_hce': nuevo_paciente.hce
        })
        
        print(f"Consulta reasignada del paciente DNI {consulta.dni} al paciente DNI {nuevo_dni}")
    
    # Actualizar la consulta con los nuevos datos
    for clave, valor in nuevos_datos.items():
        setattr(consulta, clave, valor)
    
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
    hoy_peru = obtener_fecha_peru()
    query = select(Consultas).where(
        (Consultas.anio == hoy_peru.year) &
        (Consultas.mes == hoy_peru.month) &
        (Consultas.dia == hoy_peru.day)
    )

    # Aplicar filtros opcionales
    if paciente:
        query = query.where(
            or_(
                Consultas.paciente_nombre.ilike(f"%{paciente}%"),
                Consultas.paciente_apellido.ilike(f"%{paciente}%")
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
    hoy_peru = obtener_fecha_peru()
    query = select(Consultas).where(
        (Consultas.anio == hoy_peru.year) &
        (Consultas.mes == hoy_peru.month) &
        (Consultas.dia == hoy_peru.day) &
        (Consultas.user_fullname_medic == medico_fullname)
    )

    if paciente:
        query = query.where(
            or_(
                Consultas.paciente_nombre.ilike(f"%{paciente}%"),
                Consultas.paciente_apellido.ilike(f"%{paciente}%")
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
        Consultas.user_fullname_medic == medico_fullname
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
    hoy_peru = obtener_fecha_peru()
    hace_siete_dias = hoy_peru - timedelta(days=7)

    # Suponiendo que tu modelo usa anio, mes, dia en lugar de un campo datetime completo
    query = select(func.count()).select_from(Consultas).where(
        (Consultas.user_fullname_medic == medico_fullname) &
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


def get_status_por_id_consulta(
        db:Session,
        id_consulta:int
) -> str:
    query = select (Consultas.status).where(Consultas.id == id_consulta)
    result = db.exec(query).first()
    return result or "No se encontró ninguna consulta"

def finalizar_consulta(db: Session, consulta_id: int) -> Consultas:
    consulta = db.get(Consultas, consulta_id)
    if consulta:
        consulta.status = "Terminado"
        db.add(consulta)
        db.commit()
        db.refresh(consulta)
    return consulta