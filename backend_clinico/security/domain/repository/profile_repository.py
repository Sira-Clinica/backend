from sqlmodel import Session
from sqlalchemy import select
from backend_clinico.security.domain.model.profile import Profile



class ProfileRepository:
    def create(self, db: Session, profile: Profile) -> Profile:
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

   

    def get_by_user_id(self, db: Session, user_id: int) -> Profile | None:
        statement = select(Profile).where(Profile.user_id == user_id)
        result = db.execute(statement).scalars().first()
        return result
    

    def update_null_fields(self, db: Session, user_id: int, new_data: dict) -> Profile | None:
        protected_fields = {"user_id", "full_name", "email", "area"}

        statement = select(Profile).where(Profile.user_id == user_id)
        profile = db.execute(statement).scalars().one_or_none()

        if not profile:
            return None

        for key, value in new_data.items():
            if (
                key not in protected_fields and
                hasattr(profile, key) and
                getattr(profile, key) is None and
                value is not None
            ):
                setattr(profile, key, value)

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    




