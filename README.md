# SecureVolt

## Fonctionnalités

-   **Authentification Robuste :** Inscription, connexion, et authentification à deux facteurs (TOTP/2FA).
-   **Gestion des Secrets :** Utilisation de **HashiCorp Vault** pour stocker les secrets de l'application (clé secrète, identifiants de base de données).
-   **Base de Données Professionnelle :** Utilise **PostgreSQL** pour le stockage des données.
-   **Sécurité des Formulaires :** Protection contre les attaques CSRF (anti-rejeu) et captcha simple côté serveur contre les bots.
-   **Maintenance :** Commande CLI pour détecter les comptes utilisateurs obsolètes.
-   **Déploiement Facile :** Entièrement conteneurisé avec **Docker** et orchestré par **Docker Compose**.

## Prérequis (pour Linux/Ubuntu)

-   [Docker](https://docs.docker.com/engine/install/ubuntu/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

## Installation et Lancement

1.  **Clonez le projet :**
    ```bash
    git clone <votre-url-de-repo>
    cd securevolt
    ```

2.  **Lancez tous les services (en arrière-plan) :**
    Cette commande va construire l'image de l'application et démarrer les conteneurs `app`, `vault` et `postgres`. L'application va probablement crasher une première fois, c'est normal car Vault n'est pas encore configuré.
    ```bash
    docker-compose up -d --build
    ```

3.  **Configurez les secrets dans Vault :**
    Exécutez les commandes suivantes pour stocker les secrets nécessaires au fonctionnement de l'application.

    *   **Clé secrète de l'application :**
    ```bash
    docker-compose exec vault env VAULT_ADDR='http://127.0.0.1:8200' VAULT_TOKEN='my-root-token' vault kv put secret/app SECRET_KEY="la-cle-finale-promis"
    ```

    *   **Identifiants de la base de données :**
    ```bash
    docker-compose exec vault env VAULT_ADDR='http://127.0.0.1:8200' VAULT_TOKEN='my-root-token' vault kv put secret/database DB_USER="securevolt_user" DB_PASSWORD="supersecretpassword" DB_NAME="securevolt_db" DB_HOST="postgres"
    ```

4.  **Redémarrez l'application :**
    Maintenant que les secrets sont dans Vault, redémarrez le conteneur `app` pour qu'il puisse les charger et se connecter à la base de données.
    ```bash
    docker-compose restart app
    ```

5.  **Vérifiez que tout fonctionne :**
    ```bash
    docker-compose logs -f app
    ```
    Vous devriez voir des logs indiquant que la connexion à la base de données est réussie et que le serveur Gunicorn est prêt à accepter des connexions. Appuyez sur `Ctrl+C` pour quitter les logs.

## Comment Utiliser l'Application

1.  **Accès :** Ouvrez votre navigateur et allez à l'adresse **[http://localhost:5000](http://localhost:5000)**.

2.  **Créer un compte :**
    *   Cliquez sur "S'inscrire".
    *   Pour tester, vous pouvez utiliser :
        *   **Nom d'utilisateur :** `testuser`
        *   **Mot de passe :** `Password123!`

3.  **Configurer l'OTP (2FA) avec FreeOTP :**
    *   Après l'inscription, une page affichera un **QR Code**.
    *   Ouvrez l'application **FreeOTP** (ou une autre comme Authy/Google Authenticator) sur votre téléphone.
    *   Appuyez sur l'icône pour ajouter un nouveau compte (souvent une icône de QR Code ou un `+`).
    *   Scannez le QR Code affiché dans votre navigateur.
    *   FreeOTP va automatiquement ajouter le compte "SecureVolt" et commencer à générer des codes à 6 chiffres.

4.  **Connexion :**
    *   Retournez à la page de connexion.
    *   Entrez `testuser` et `Password123!`.
    *   Répondez à la simple question mathématique (captcha).
    *   Sur l'écran suivant, entrez le code à 6 chiffres actuellement affiché par FreeOTP.
    *   Vous voilà sur votre tableau de bord !

## Commandes de Maintenance

Pour lister les utilisateurs inactifs depuis plus de 90 jours (par défaut) :
```bash
docker-compose exec app flask list-obsolete-users
```
Pour spécifier un nombre de jours différent :
```bash
docker-compose exec app flask list-obsolete-users --days=30
```

## Arrêter l'Application

Pour arrêter tous les conteneurs et supprimer les réseaux créés :
```bash
docker-compose down
```
Pour également supprimer le volume de la base de données (perte de toutes les données !) :
```bash
docker-compose down -v
```