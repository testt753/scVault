# Étape 1: Utiliser une image Python officielle et légère
FROM python:3.10-slim

# Étape 2: Définir un répertoire de travail propre.
WORKDIR /code

# Étape 3: Copier le fichier des dépendances
COPY requirements.txt .

# Étape 4: Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5: Copier TOUT le code du projet dans le WORKDIR
COPY . .

# Étape 6: Commande pour lancer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]