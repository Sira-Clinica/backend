from sqlmodel import Session, select
from typing import List, Optional
from backend_clinico.security.domain.model.account_request import AccountRequest

class AccountRequestRepository:
    def create(self, db: Session, request: AccountRequest) -> AccountRequest:
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    def get_pending(self, db: Session) -> List[AccountRequest]:
        return db.exec(select(AccountRequest).where(AccountRequest.status == "pendiente")).all()

    def get_by_id(self, db: Session, request_id: int) -> Optional[AccountRequest]:
        return db.get(AccountRequest, request_id)

    def update_status(self, db: Session, request: AccountRequest, status: str) -> AccountRequest:
        request.status = status
        db.add(request)
        db.commit()
        db.refresh(request)
        return request
    
    def get_not_accepted(self, db: Session) -> List[AccountRequest]:
        return db.exec(
            select(AccountRequest).where(AccountRequest.status != "aceptado")
        ).all()
