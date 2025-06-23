from sqlmodel import Session, select
from typing import Optional, List
from backend_clinico.security.domain.model.user import User
from sqlalchemy.orm import selectinload


class UserRepository:

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()


    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.exec(select(User).where(User.email == email)).first()

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    def get_all(self, db: Session) -> List[User]:
        return db.exec(select(User)).all()

    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()
