from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

class RegisterForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired(), Length(min=4, max=100)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('S\'inscrire')

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    captcha = IntegerField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Suivant')

class TokenForm(FlaskForm):
    token = StringField('Code à 6 chiffres', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Vérifier')

class PasswordEntryForm(FlaskForm):
    site_name = StringField('Nom du site', validators=[DataRequired()])
    username = StringField('Identifiant', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Ajouter')