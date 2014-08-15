from flask.ext.wtf import Form
from wtforms import TextField, SubmitField
from wtforms.validators import Required


class EditForm(Form):
    name = TextField('name', validators=[Required()])
    save = SubmitField('save')
