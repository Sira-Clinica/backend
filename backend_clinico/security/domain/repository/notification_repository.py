from sqlmodel import Session, select
from backend_clinico.security.domain.model.notification import Notification

class NotificationRepository:
    def create(self, db: Session, message: str) -> Notification:
        notif = Notification(message=message)
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif
    
    def get_all(self, db: Session) -> list[Notification]:
        statement = select(Notification)
        return db.execute(statement).scalars().all()

    def delete_by_id(self, db: Session, notif_id: int) -> bool:
        notif = db.get(Notification, notif_id)
        if not notif:
            return False
        db.delete(notif)
        db.commit()
        return True
