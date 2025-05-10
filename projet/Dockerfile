# Image de base officielle Python
FROM python:3.11-slim

# Dossier de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 8080

# Commande pour lancer l'application
CMD ["python", "app.py"]