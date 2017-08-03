from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,\
ValidationError
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Эл. адрес', validators=[Required(), Length(1, 64),
                                        Email("Недопустимый Эл. адрес!")])
    password = PasswordField('Пароль', validators=[Required()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    email = StringField('Эл. адрес', validators=[Required(), Length(1, 64),
                                        Email("Недопустимый Эл. адрес!")])
    username = StringField('Имя', validators=[Required(), Length(1, 64),
                Regexp('^[A-Za-zА-Яа-я][A-Za-z0-9_.А-Яа-я0-9_.]*$', 0,
        'Имя должно содержать только буквы, цифры, точки или подчеркивания.')])
    password = PasswordField('Пароль', validators=[Required(),
                    EqualTo('password2', message="Пароли должны совпадать.")])
    password2 = PasswordField('Подтвердите пароль', validators=[Required()])
    submit = SubmitField('Регистрация')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Эл. адрес уже зарегистрирован.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Пользователь с таким именем уже существует.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[Required()])
    password = PasswordField('Новый пароль', validators=[Required(),
                    EqualTo('password2', message='Пароли должны совпадать.')])
    password2 = PasswordField('Подтвердите новый пароль',
                              validators=[Required()])
    submit = SubmitField('Изменить пароль')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Эл. адрес', validators=[Required(), Length(1, 64),
                                            Email("Недопустимый Эл. адрес!")])
    submit = SubmitField('Сбросить пароль')


class PasswordResetForm(FlaskForm):
    email = StringField('Эл. адрес', validators=[Required(), Length(1, 64),
                                            Email("Недопустимый Эл. адрес!")])
    password = PasswordField('Новый Пароль', validators=[Required(),
                    EqualTo('password2', message='Пароли должны совпадать.')])
    password2 = PasswordField('Подтвердите пароль', validators=[Required()])
    submit = SubmitField('Сбросить пароль')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Неизвестный эл. адрес.')


class ChangeEmailForm(FlaskForm):
    email = StringField('Новый эл. адрес', validators=[Required(),
                        Length(1, 64), Email("Недопустимый Эл. адрес!")])
    password = PasswordField('Пароль', validators=[Required()])
    submit = SubmitField('Изменить эл. адрес')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Такой эл. адрес уже существует.')
