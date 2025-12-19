# Utiliser une version légère et optimisée de l'image Python
FROM python:3.9-slim

# Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Copier uniquement les fichiers nécessaires dans le conteneur
COPY requirements.txt .
COPY . .

# Installer les dépendances système nécessaires (si applicables)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python à partir de requirements.txt
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; fi

# Installer le projet lui-même (si setup.py est présent)
RUN if [ -f "setup.py" ]; then pip install -e .; fi

# Définir la commande par défaut pour exécuter l’application
CMD ["python", "app.py"]