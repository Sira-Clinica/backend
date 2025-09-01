# config.py


from pydantic import Field, ValidationError
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Cargar variables desde el archivo .env (si existe)
load_dotenv()

class Settings(BaseSettings):


    # Configuración de base de datos
    database_url: str = Field(..., env="DATABASE_URL")
    

    # Configuración de usuario administrador inicial
    initial_admin_username: str = Field(..., env="INITIAL_ADMIN_USERNAME")
    initial_admin_email: str = Field(..., env="INITIAL_ADMIN_EMAIL")
    initial_admin_full_name: str = Field(..., env="INITIAL_ADMIN_FULL_NAME")
    initial_admin_password: str = Field(..., env="INITIAL_ADMIN_PASSWORD")

    # Configuración de autenticación
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(..., env="ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")


    email_host: str = Field(..., env="EMAIL_HOST")
    email_port: int = Field(..., env="EMAIL_PORT")
    email_host_user: str = Field(..., env="EMAIL_HOST_USER")
    email_host_password: str = Field(..., env="EMAIL_HOST_PASSWORD")
    email_use_tls: bool = Field(..., env="EMAIL_USE_TLS")




    class Config:
        env_file = ".env"  # Indica que se lean variables desde el archivo .env
        env_file_encoding = "utf-8"  # Asegura correcta lectura de caracteres especiales

try:
    settings = Settings()
except ValidationError as e:
    print("Error loading settings: %s", e.json())
    raise
