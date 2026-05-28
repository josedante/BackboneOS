# Dockerfile para Django
FROM python:3.13-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (curl for Node.js Tailwind build)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        postgresql-server-dev-all \
        libpq-dev \
        build-essential \
        gcc \
        python3-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Build Tailwind CSS at image build (dev compose volume may override static/dist)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && npm ci \
    && npm run tailwind:build

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]