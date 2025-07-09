import click
from datetime import datetime, timedelta
from flask.cli import with_appcontext
from app import create_app, db
from app.models import User

app = create_app()

@app.cli.command("list-obsolete-users")
@click.option('--days', default=90, help='Nombre de jours d\'inactivité pour considérer un compte comme obsolète.')
@with_appcontext
def list_obsolete_users(days):
    """Liste les utilisateurs qui ne se sont pas connectés depuis un certain nombre de jours."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    obsolete_users = User.query.filter(
        (User.last_login_at < cutoff_date) | (User.last_login_at == None)
    ).all()

    if not obsolete_users:
        print(f"Aucun compte obsolète trouvé (inactif depuis plus de {days} jours).")
        return

    print(f"--- Comptes inactifs depuis plus de {days} jours ---")
    for user in obsolete_users:
        last_login_str = user.last_login_at.strftime('%Y-%m-%d') if user.last_login_at else "Jamais connecté"
        print(f"ID: {user.id}, Username: {user.username}, Dernière connexion: {last_login_str}")
    print("--------------------------------------------------")

if __name__ == '__main__':
    app.run()
