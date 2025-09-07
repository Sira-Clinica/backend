# Imagen base estable y compatible con torch y sentence-transformers
FROM python:3.11-slim

# Evitar mensajes interactivos y mejorar logging
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libffi-dev \
    libssl-dev \
    python3-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /code

# Copiar solo requirements primero para aprovechar cache
COPY ./requirements.txt .

# Actualizar pip y herramientas de instalación
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias de Python (con preferencia a binarios precompilados)
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copiar código fuente (esto invalida cache solo si cambias tu código)
COPY ./backend_clinico ./backend_clinico
COPY ./main.py .

# Exponer puerto para FastAPI
EXPOSE 8080

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

