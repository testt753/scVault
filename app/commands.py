import click
from datetime import datetime, timedelta
from .models import User

command_bp = click.Group('users')

@command_bp.command("list-obsolete")
@click.option('--days', default=90, help='Nombre de jours d\'inactivité pour considérer un compte comme obsolète.')
def list_obsolete_users(days):
    """Liste les utilisateurs qui ne se sont pas connectés depuis X jours."""
    from . import db
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    obsolete_users = User.query.filter(
        (User.last_login_at < cutoff_date) | (User.last_login_at == None)
    ).all()

    if not obsolete_users:
        click.echo(f"Aucun compte obsolète trouvé (inactif depuis plus de {days} jours).")
        return

    click.echo(f"--- Comptes inactifs depuis plus de {days} jours ---")
    for user in obsolete_users:
        last_login_str = user.last_login_at.strftime('%Y-%m-%d') if user.last_login_at else "Jamais connecté"
        click.echo(f"ID: {user.id}, Username: {user.username}, Dernière connexion: {last_login_str}")
    click.echo("--------------------------------------------------")
