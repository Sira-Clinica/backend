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
    

    def get_medicos(self, db: Session) -> List[User]:
        return db.exec(select(User).where(User.role_id == 2)).all()


    def update(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()






def send_credentials_email(to_email: str, username: str, password: str):
    subject = "Bienvenido/a a SIRA – Tu cuenta ha sido creada"
    
    # Template HTML
    html_body = f"""
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="color-scheme" content="light only" />
        <title>Bienvenido/a a SIRA – Tu cuenta ha sido creada</title>
        <style>
          /* Paleta alineada con tu app:
             slate-50 #f8fafc, slate-200 #e2e8f0, slate-500 #64748b, slate-800 #1e293b
             blue-600 #2563eb, indigo-500 #6366f1, indigo-50 #eef2ff */
          body {{
            margin: 0;
            padding: 0;
            background: #f8fafc; /* slate-50 */
            color: #1e293b; /* slate-800 */
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, "Noto Sans", "Helvetica Neue", sans-serif;
          }}
          .wrapper {{
            width: 100%;
            table-layout: fixed;
            background: #f8fafc;
            padding: 24px 0;
          }}
          .container {{
            max-width: 640px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            border: 1px solid #e2e8f0; /* slate-200 */
            box-shadow: 0 20px 60px rgba(2, 6, 23, 0.12);
            overflow: hidden;
          }}
          .hero {{
            padding: 28px 28px 24px;
            color: #ffffff;
            background: linear-gradient(90deg, #2563eb 0%, #6366f1 100%); /* blue-600 -> indigo-500 */
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          }}
          .kicker {{
            margin: 0 0 6px;
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.9;
          }}
          h1 {{
            margin: 0;
            font-size: 24px;
            line-height: 1.25;
            font-weight: 800;
          }}
          .subhead {{
            margin: 6px 0 0;
            font-size: 14px;
            opacity: 0.9;
          }}
          .content {{
            padding: 24px 28px 8px;
            color: #1e293b; /* slate-800 */
          }}
          p {{
            margin: 0 0 12px;
            font-size: 15px;
            line-height: 1.6;
            color: #1e293b;
          }}
          .credentials {{
            margin: 16px 0 20px;
            padding: 14px 16px;
            border-radius: 12px;
            background: #eef2ff; /* indigo-50 */
            border: 1px solid #e2e8f0; /* slate-200 */
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            color: #1e293b;
          }}
          .button-row {{
            padding: 0 28px 28px;
          }}
          .btn {{
            display: inline-block;
            padding: 12px 20px;
            background: #2563eb; /* blue-600 */
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 14px;
          }}
          .btn:focus,
          .btn:hover {{
            background: #1d4ed8; /* approx blue-700 */
          }}
          .footer {{
            border-top: 1px solid #e2e8f0; /* slate-200 */
            padding: 16px 28px 24px;
            text-align: center;
            color: #64748b; /* slate-500 */
            font-size: 13px;
          }}
          .footer a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
          }}
          .footer a:hover {{ text-decoration: underline; }}
          @media (max-width: 480px) {{
            .container {{ border-radius: 0; }}
            .hero, .content, .button-row, .footer {{ padding-left: 18px; padding-right: 18px; }}
            h1 {{ font-size: 22px; }}
          }}
        </style>
      </head>
      <body>
        <div class="wrapper">
          <div class="container">
            <!-- HERO -->
            <div class="hero">
              <div class="kicker">SIRA • Salud Respiratoria</div>
              <h1>¡Bienvenido/a a SIRA, {username}!</h1>
              <div class="subhead">Tu cuenta ha sido creada con éxito.</div>
            </div>

            <!-- CONTENT -->
            <div class="content">
              <p>Nos alegra tenerte con nosotros. A continuación encontrarás tus credenciales de acceso:</p>
              <div class="credentials">
                <div><strong>Usuario:</strong> {username}</div>
                <div><strong>Contraseña temporal:</strong> {password}</div>
              </div>
              <p>Por motivos de seguridad, inicia sesión y cambia tu contraseña lo antes posible.</p>
            </div>

            <!-- CTA -->
            <div class="button-row">
              <a class="btn" href="https://tusitio.com/login" target="_blank" rel="noopener">Iniciar sesión</a>
            </div>

            <!-- FOOTER -->
            <div class="footer">
              ¿Necesitas ayuda? Escríbenos a
              <a href="mailto:sira.salud.respiratoria@gmail.com">sira.salud.respiratoria@gmail.com</a><br />
              <strong>Equipo SIRA</strong>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    
    # Versión de texto plano como fallback
    plain_body = f"""
    Hola {username},

    Tu cuenta ha sido creada exitosamente en SIRA.

    Usuario: {username}
    Contraseña temporal: {password}

    Por favor, inicia sesión y cambia tu contraseña lo antes posible.

    ¿Necesitas ayuda? Escríbenos a sira.salud.respiratoria@gmail.com

    Saludos,
    Equipo SIRA
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Adjuntar tanto la versión de texto plano como la HTML
    part1 = MIMEText(plain_body, "plain", "utf-8")
    part2 = MIMEText(html_body, "html", "utf-8")
    
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, to_email, msg.as_string())
        server.quit()
        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


def send_password_change_email(to_email: str, username: str, new_password: str):
    subject = "SIRA – Tu contraseña ha sido actualizada"
    
    # Template HTML para cambio de contraseña
    html_body = f"""
    <html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="color-scheme" content="light only" />
        <title>SIRA – Tu contraseña ha sido actualizada</title>
        <style>
          /* Mismos estilos que antes */
          body {{
            margin: 0;
            padding: 0;
            background: #f8fafc;
            color: #1e293b;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, "Noto Sans", "Helvetica Neue", sans-serif;
          }}
          .wrapper {{
            width: 100%;
            table-layout: fixed;
            background: #f8fafc;
            padding: 24px 0;
          }}
          .container {{
            max-width: 640px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 20px 60px rgba(2, 6, 23, 0.12);
            overflow: hidden;
          }}
          .hero {{
            padding: 28px 28px 24px;
            color: #ffffff;
            background: linear-gradient(90deg, #2563eb 0%, #6366f1 100%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          }}
          .kicker {{
            margin: 0 0 6px;
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.9;
          }}
          h1 {{
            margin: 0;
            font-size: 24px;
            line-height: 1.25;
            font-weight: 800;
          }}
          .subhead {{
            margin: 6px 0 0;
            font-size: 14px;
            opacity: 0.9;
          }}
          .content {{
            padding: 24px 28px 8px;
            color: #1e293b;
          }}
          p {{
            margin: 0 0 12px;
            font-size: 15px;
            line-height: 1.6;
            color: #1e293b;
          }}
          .credentials {{
            margin: 16px 0 20px;
            padding: 14px 16px;
            border-radius: 12px;
            background: #eef2ff;
            border: 1px solid #e2e8f0;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            color: #1e293b;
          }}
          .button-row {{
            padding: 0 28px 28px;
          }}
          .btn {{
            display: inline-block;
            padding: 12px 20px;
            background: #2563eb;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 14px;
          }}
          .btn:focus,
          .btn:hover {{
            background: #1d4ed8;
          }}
          .footer {{
            border-top: 1px solid #e2e8f0;
            padding: 16px 28px 24px;
            text-align: center;
            color: #64748b;
            font-size: 13px;
          }}
          .footer a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
          }}
          .footer a:hover {{ text-decoration: underline; }}
          .alert {{
            margin: 16px 0;
            padding: 14px 16px;
            border-radius: 12px;
            background: #fef3c7;
            border: 1px solid #f59e0b;
            color: #92400e;
            font-size: 14px;
          }}
          @media (max-width: 480px) {{
            .container {{ border-radius: 0; }}
            .hero, .content, .button-row, .footer {{ padding-left: 18px; padding-right: 18px; }}
            h1 {{ font-size: 22px; }}
          }}
        </style>
      </head>
      <body>
        <div class="wrapper">
          <div class="container">
            <!-- HERO -->
            <div class="hero">
              <div class="kicker">SIRA • Salud Respiratoria</div>
              <h1>Contraseña actualizada, {username}</h1>
              <div class="subhead">Tu contraseña ha sido cambiada exitosamente.</div>
            </div>

            <!-- CONTENT -->
            <div class="content">
              <div class="alert">
                <strong>⚠️ Importante:</strong> Tu contraseña ha sido actualizada por motivos de seguridad.
              </div>
              
              <p>Tus nuevas credenciales de acceso son:</p>
              <div class="credentials">
                <div><strong>Usuario:</strong> {username}</div>
                <div><strong>Nueva contraseña:</strong> {new_password}</div>
              </div>
              
              <p>Si no realizaste este cambio, contacta inmediatamente a nuestro equipo de soporte.</p>
              <p>Te recomendamos cambiar esta contraseña por una personalizada tras tu próximo inicio de sesión.</p>
            </div>

            <!-- CTA -->
            <div class="button-row">
              <a class="btn" href="https://tusitio.com/login" target="_blank" rel="noopener">Iniciar sesión</a>
            </div>

            <!-- FOOTER -->
            <div class="footer">
              ¿Necesitas ayuda? Escríbenos a
              <a href="mailto:sira.salud.respiratoria@gmail.com">sira.salud.respiratoria@gmail.com</a><br />
              <strong>Equipo SIRA</strong>
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    
    # Versión de texto plano como fallback
    plain_body = f"""
    Hola {username},

    Tu contraseña en SIRA ha sido actualizada exitosamente.

    Tus nuevas credenciales son:
    Usuario: {username}
    Nueva contraseña: {new_password}

    Si no realizaste este cambio, contacta inmediatamente a nuestro equipo de soporte.
    Te recomendamos cambiar esta contraseña por una personalizada tras tu próximo inicio de sesión.

    ¿Necesitas ayuda? Escríbenos a sira.salud.respiratoria@gmail.com

    Saludos,
    Equipo SIRA
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_HOST_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    # Adjuntar tanto la versión de texto plano como la HTML
    part1 = MIMEText(plain_body, "plain", "utf-8")
    part2 = MIMEText(html_body, "html", "utf-8")
    
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, to_email, msg.as_string())
        server.quit()
        print(f"Correo de cambio de contraseña enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar correo de cambio de contraseña: {e}")
