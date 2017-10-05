from flask import render_template, redirect, request, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from config import Auth
from . import auth
from ..models import User
from ..email import send_email
from .. import db, login_manager
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Вы успешно вошли в свой аккаунт.")
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Неверная почта или пароль.')
    return render_template('auth/login.html', form=form, auth_url=auth_url)


@auth.route('/login_auth', methods=['GET', 'POST'])
def login_auth():
    if current_user is not None and current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('main.index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'Доступ запрещен.'
        return 'Обнаружена ошибка.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('auth.login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return repr(HTTPError)
        google = get_google_auth(token=token)
        resp = google.get(
        "https://www.googleapis.com/plus/v1/people/me?access_token={}"
        .format(token))
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['emails'][0]['value']
            username = user_data['name']['givenName']
            user = User.query.filter_by(email=email).first()
            if user is None:
                check_username = False
                count = 1
                new_username = username
                while not check_username:
                    user = User.query.filter_by(username=new_username).firts()
                    if user is not None:
                        new_username = username + "{}".format(count)
                        count += 1
                    else:
                        check_username = True
                user = User(email=email,
                            username=new_username,
                            tokens=json.dumps(token),
                            confirmed=True)
                db.session.add(user)
                db.session.commit()
                flash('Вы успешно зарегестрировались через google+.')
            flash("Вы успешно вошли в свой аккаунт.")
            login_user(user)
            return redirect(request.args.get('next') or url_for('main.index'))
        return 'Не удалось получить Вашу информацию.'


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
                Auth.CLIENT_ID,
                state=state,
                redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из своей учетной записи.")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Подтвердите аккаунт', 'auth/email/confirm',
                   user=user, token=token)
        flash('Письмо подтверждения было отправленно Вам на почту.')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('Вы подтвердили свой аккаунт. Спасибо!')
    else:
        flash('Ссылка подтверждения неверная или срок ее действия истек.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Подтвердите аккаунт', 'auth/email/confirm',
               user=current_user, token=token)
    flash('Новое письмо было отправленно Вам на почту.')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Ваш пароль был обновлен.')
            return redirect(url_for('main.index'))
        else:
            flash('Неверный пароль.')
    return render_template('auth/change_password.html', form=form)



@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Сброс пароля', 'auth/email/reset_password',
                       user=user, token=token, next=request.args.get('next'))
        flash('Письмо с инструкциями по сбросу пароля было выслано на Ваш эл. адрес.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redierct(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Ваш пароль был обновлен.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Подтвердите эл. адрес',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash("Письмо с инструкциями по подтверждению Вашего новго эл."
                  " адреса было выслано.")
            return redirect(url_for('main.index'))
        else:
            flash('Неверный эл. адрес или пароль.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Ваш эл. адрес был изменен.')
    else:
        flash('Неверный запрос.')
    return redirect(url_for('main.index'))
