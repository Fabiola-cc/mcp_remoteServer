FROM python:3.11-slim

WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY sleep_advice_server.py .

# Variables de entorno
ENV RUN_MODE=web
ENV PORT=8000

# Exponer puerto
EXPOSE 8000

# Comando para iniciar
CMD ["python", "sleep_advice_server.py"]
