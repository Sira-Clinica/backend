from fastapi import APIRouter
from backend_clinico.app.controllers.predict_controller import predict_router
from backend_clinico.security.interfaces.rest.auth_controller import router_auth
from backend_clinico.security.interfaces.rest.role_controller import router_role
from backend_clinico.security.interfaces.rest.user_controller import router_user
from backend_clinico.app.controllers.vitalsign_controller import vitalsign_router
from backend_clinico.app.controllers.paciente_controller import paciente_router
from backend_clinico.app.controllers.historialclinico_controller import historial_router
from backend_clinico.app.controllers.consulta_controller import consulta_router
from backend_clinico.security.interfaces.rest.account_request_controller import router_account
from backend_clinico.security.interfaces.rest.profile_controller import router_profile
from backend_clinico.security.interfaces.rest.notification_controller import router_notification
router = APIRouter()
router.include_router(predict_router, prefix="/api/v1", tags=["Diagnóstico"])
router.include_router(router_auth, prefix="/api/v1", tags=["Autenticación"])
router.include_router(router_role, prefix="/api/v1", tags=["Roles"])
router.include_router(router_user, prefix="/api/v1", tags=["Usuarios"])
router.include_router(vitalsign_router, prefix="/api/v1", tags=["Signos Vitales"])
router.include_router(paciente_router, prefix="/api/v1", tags=["Pacientes"])
router.include_router(historial_router, prefix="/api/v1", tags=["Historial Clínico"])
router.include_router(consulta_router,prefix="/api/v1", tags=["Consultas"])
router.include_router(router_account, prefix="/api/v1", tags=["Solicitudes de cuenta"])
router.include_router(router_profile, prefix="/api/v1", tags=["Profiles"])
router.include_router(router_notification, prefix="/api/v1", tags=["Notificaciones"])