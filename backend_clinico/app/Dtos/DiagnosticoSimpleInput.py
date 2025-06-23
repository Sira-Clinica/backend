# backend_clinico/app/Dtos/DiagnosticoSimpleInput.py
from pydantic import BaseModel

class DiagnosticoSimpleInput(BaseModel):
    motivo_consulta: str
    examenfisico: str
