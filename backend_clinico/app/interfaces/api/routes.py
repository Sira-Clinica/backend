from fastapi import APIRouter
from backend_clinico.app.controllers.predict_controller import predict_router
from backend_clinico.security.interfaces.rest.auth_controller import router_auth
from backend_clinico.security.interfaces.rest.role_controller import router_role
from backend_clinico.security.interfaces.rest.user_controller import router_user
from backend_clinico.app.controllers.vitalsign_controller import vitalsign_router
from backend_clinico.app.controllers.paciente_controller import paciente_router
from backend_clinico.app.controllers.historialclinico_controller import historial_router
router = APIRouter()
router.include_router(predict_router, prefix="/api/v1", tags=["Diagnóstico"])
router.include_router(router_auth, prefix="/api/v1", tags=["Autenticación"])
router.include_router(router_role, prefix="/api/v1", tags=["Roles"])
router.include_router(router_user, prefix="/api/v1", tags=["Usuarios"])
router.include_router(vitalsign_router, prefix="/api/v1", tags=["Signos Vitales"])
router.include_router(paciente_router, prefix="/api/v1", tags=["Pacientes"])
router.include_router(historial_router, prefix="/api/v1", tags=["Historial Clínico"])