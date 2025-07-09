from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    otp_secret = db.Column(db.String(32), nullable=False)
    last_login_at = db.Column(db.DateTime, nullable=True, default=None)

    passwords = db.relationship('PasswordEntry', backref='owner', lazy=True)

class PasswordEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    # On utilise un simple texte pour la démo.  
    password = db.Column(db.String(255), nullable=False) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)