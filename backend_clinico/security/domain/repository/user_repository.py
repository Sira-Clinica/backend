from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select
from typing import Optional, List
from backend_clinico.app.core.config import settings
from backend_clinico.security.domain.model.user import User
from sqlalchemy.orm import selectinload
import smtplib
from email.mime.text import MIMEText

EMAIL_HOST = settings.email_host
EMAIL_HOST_PASSWORD = settings.email_host_password
EMAIL_HOST_USER = settings.email_host_user
EMAIL_PORT = settings.email_port
EMAIL_USE_TLS = settings.email_use_tls

class UserRepository:



    def get_by_username(self, db: Session, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return db.exec(statement).first()


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




def send_credentials_email(to_email: str, username: str, password: str):
        subject = "Tu cuenta ha sido creada"
        body = f"""
        Hola,

        Tu cuenta ha sido creada exitosamente.

        Usuario: {username}
        Contraseña: {password}

        Por favor, inicia sesión y cambia tu contraseña lo antes posible.

        Saludos,
        Equipo de Administración
        """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_HOST_USER
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, to_email, msg.as_string())
            server.quit()
            print(f"Correo enviado a {to_email}")
        except Exception as e:
            print(f"Error al enviar correo: {e}")


