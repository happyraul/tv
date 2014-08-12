from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required


class EditForm(Form):
    name = TextField('name', validators=[Required()])
