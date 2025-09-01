from backend_clinico.app.models.domain.Diagnostico import Diagnostico
from backend_clinico.app.models.domain.HistorialClinico import HistorialClinico
from sqlmodel import Session, select

from backend_clinico.app.models.domain.Paciente import Paciente
def guardar_en_historial_clinico(db: Session, diagnostico: Diagnostico, paciente: Paciente):
    entrada = HistorialClinico(
        paciente_dni=paciente.dni,
        paciente_nombre=paciente.nombre,
        temperatura=diagnostico.temperatura,
        edad=diagnostico.edad,
        f_card=diagnostico.f_card,
        f_resp=diagnostico.f_resp,
        talla=diagnostico.talla,
        peso=diagnostico.peso,
        genero=diagnostico.genero,
        motivo_consulta=diagnostico.motivo_consulta,
        examenfisico=diagnostico.examenfisico,
        indicaciones=diagnostico.indicaciones,
        medicamentos=diagnostico.medicamentos,
        notas=diagnostico.notas,
        resultado_diagnostico=diagnostico.resultado,
    )
    db.add(entrada)
    db.commit()
    db.refresh(entrada)


def obtener_historial_por_dni(db: Session, dni: str) -> list[HistorialClinico]:
    return db.exec(
        select(HistorialClinico)
        .where(HistorialClinico.paciente_dni == dni)
        .order_by(HistorialClinico.fecha_registro.desc())
    ).all()
