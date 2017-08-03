from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(FlaskForm):
    name = StringField('Как тебя зовут?', validators=[Required()])
    submit = SubmitField('Принять')
