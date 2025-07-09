import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from .utils import get_secret_from_vault

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Application Factory
def create_app():
    app = Flask(__name__)

    print("Tentative de configuration de l'application depuis Vault...")

    # 1. Récupérer la clé secrète de l'application
    app.config['SECRET_KEY'] = get_secret_from_vault('app', 'SECRET_KEY')
    if not app.config['SECRET_KEY']:
        print("ERREUR CRITIQUE: Impossible de récupérer 'SECRET_KEY' depuis Vault. Arrêt.")
        sys.exit(1)

    # 2. Récupérer les identifiants de la base de données
    db_user = get_secret_from_vault('database', 'DB_USER')
    db_pass = get_secret_from_vault('database', 'DB_PASSWORD')
    db_host = get_secret_from_vault('database', 'DB_HOST')
    db_name = get_secret_from_vault('database', 'DB_NAME')

    if not all([db_user, db_pass, db_host, db_name]):
        print("ERREUR CRITIQUE: Il manque des identifiants de base de données dans Vault. Arrêt.")
        sys.exit(1)
        
    # 3. Construire l'URI de la base de données
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    print("Configuration depuis Vault réussie.")
    
    # Lier les extensions à l'application
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .commands import command_bp
    app.cli.add_command(command_bp)

    with app.app_context():
        db.create_all()

    return app