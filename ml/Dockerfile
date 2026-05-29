# ============================================================
# Dockerfile para el servicio de Machine Learning (Flask API)
# ============================================================

# Imagen base con Python 3.11
FROM python:3.11-slim

# Establecer variables de entorno para evitar prompts de install
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para las librerías ML
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente y los modelos
COPY predict.py .
COPY models/ models/

# Exponer el puerto de la API
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "predict:app"]