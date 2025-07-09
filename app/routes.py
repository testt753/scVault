from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import random
from . import db, bcrypt
from .models import User, PasswordEntry
from .utils import generate_qr_code
from flask_login import login_user, logout_user, login_required, current_user
import pyotp
from datetime import datetime
from .forms import RegisterForm, LoginForm, TokenForm, PasswordEntryForm

main = Blueprint('auth', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Ce nom d\'utilisateur existe déjà.')
            return redirect(url_for('auth.register'))

        otp_secret = pyotp.random_base32()
        
        new_user = User(
            username=username,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            otp_secret=otp_secret
        )

        db.session.add(new_user)
        db.session.commit()

        session['otp_secret_for_setup'] = otp_secret
        session['username_for_setup'] = username
        return redirect(url_for('auth.setup_2fa'))

    return render_template('register.html', form=form)

@main.route('/setup-2fa')
def setup_2fa():
    otp_secret = session.get('otp_secret_for_setup')
    username = session.get('username_for_setup')
    if not otp_secret or not username:
        return redirect(url_for('auth.register'))

    totp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(
        name=username,
        issuer_name='SecureVolt'
    )
    qr_code = generate_qr_code(totp_uri)
    
    # Nettoyer la session
    session.pop('otp_secret_for_setup', None)
    session.pop('username_for_setup', None)

    return render_template('setup_2fa.html', qr_code=qr_code)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        session['captcha_answer'] = num1 + num2
    
    captcha_question = f"Combien font {session.get('captcha_answer', 0) - random.randint(1,5)} + {random.randint(1,5)} ?" # un peu obscurci pour l'exemple
    if 'captcha_answer' in session:
        captcha_question = "Veuillez résoudre le calcul."


    if form.validate_on_submit():
        user_answer = form.captcha.data
        correct_answer = session.pop('captcha_answer', None) 

        if user_answer != correct_answer:
            flash('Réponse du Captcha incorrecte.')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            session['user_id_for_2fa'] = user.id
            return redirect(url_for('auth.login_2fa'))
        else:
            flash('Identifiants incorrects. Veuillez réessayer.')
            return redirect(url_for('auth.login'))

    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_answer'] = num1 + num2
    captcha_question = f"Combien font {num1} + {num2} ?"

    return render_template('login.html', form=form, captcha_question=captcha_question)

@main.route('/login/2fa', methods=['GET', 'POST'])
def login_2fa():
    user_id = session.get('user_id_for_2fa')
    if not user_id:
        return redirect(url_for('auth.login'))

    form = TokenForm()
    if form.validate_on_submit():
        token = form.token.data
        user = User.query.get(user_id)
        
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(token):
            login_user(user, remember=True)
            session.pop('user_id_for_2fa', None)

            user.last_login_at = datetime.utcnow()
            db.session.commit()

            return redirect(url_for('auth.dashboard'))
        else:
            flash('Code 2FA invalide.')
            return redirect(url_for('auth.login_2fa'))

    return render_template('login_2fa.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = PasswordEntryForm()
    if form.validate_on_submit():
        new_entry = PasswordEntry(
            site_name=form.site_name.data,
            username=form.username.data,
            password=form.password.data,
            owner=current_user
        )
        db.session.add(new_entry)
        db.session.commit()
        flash('Entrée ajoutée avec succès !')
        return redirect(url_for('auth.dashboard'))

    passwords = PasswordEntry.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', name=current_user.username, passwords=passwords, form=form)