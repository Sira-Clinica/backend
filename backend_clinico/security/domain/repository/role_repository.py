from sqlmodel import Session, select
from typing import Optional, List
from backend_clinico.security.domain.model.role import Role


class RoleRepository:

    
    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        return db.exec(select(Role).where(Role.name == name)).first()
  
    def get_all(self, db: Session) -> List[Role]:
        return db.exec(select(Role)).all()
   
    def create(self, db: Session, role: Role) -> Role:
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
