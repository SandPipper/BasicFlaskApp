from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('Как тебя зовут?', validators=[Required()])
    submit = SubmitField('Submit')
