# ── Stage unique : image de production ────────────────────────────────────────
FROM python:3.12-slim

# Dépendances système nécessaires pour certains packages Python
# (asyncpg, Pillow, reportlab, llvmlite/numba pour ONNX)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les dépendances Python en premier
# (couche Docker cachée si requirements.txt ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 300 --retries 5 -r requirements.txt

# Copier le code de l'application
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY docker_init.py .

# Créer le dossier uploads (monté en volume en production)
RUN mkdir -p /app/uploads

# Port exposé par uvicorn
EXPOSE 8000

# Lancement : applique les migrations Alembic puis démarre uvicorn
CMD ["sh", "-c", "python docker_init.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
