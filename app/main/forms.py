from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, TextAreaField, SubmitField, BooleanField,\
                    SelectField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from ..models import Role, User


class EditProfileForm(FlaskForm):
    name = StringField('Ваши реальные имя и фамилия',
                        validators=[Length(0, 64)])
    location = StringField('Ваше местонахождение(город и страна)',
                            validators=[Length(0, 64)])
    about_me = TextAreaField('Обо мне')
    submit = SubmitField('Принять')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Эл. адрес', validators=[Required(), Length(1, 64),
                                     Email("Недопустимый Эл. адрес!")])
    username = StringField('Имя', validators=[Required(), Length(1, 64),
                Regexp('^[A-Za-zА-Яа-я][A-Za-z0-9_.А-Яа-я0-9_.]*$', 0,
        'Имя должно содержать только буквы, цифры, точки или подчеркивания.')])
    confirmed = BooleanField('Подтвержденный')
    role = SelectField('Роль', coerce=int)
    name = StringField('Реальное имя и фамилия', validators=[Length(0, 64)])
    location = StringField('Местоположене', validators=[Length(0, 64)])
    about_me = TextAreaField('Обо мне')
    submit = SubmitField('Принять')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Эл. адрес уже зарегистрирован.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Пользователь с таким именем уже существует.')


class PostForm(FlaskForm):
    body = PageDownField('Что напишешь сегодня?', validators=[Required()])
    submit = SubmitField('Принять')


class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Принять')
