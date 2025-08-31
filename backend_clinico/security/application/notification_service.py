from sqlmodel import Session
from backend_clinico.security.domain.repository.notification_repository import NotificationRepository

class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def mostrar_todo(self, db: Session):
        return self.repository.get_all(db)

    def eliminar_por_id(self, db: Session, notif_id: int):
        deleted = self.repository.delete_by_id(db, notif_id)
        if not deleted:
            raise ValueError(f"No se encontró la notificación con id {notif_id}")
        return deleted
