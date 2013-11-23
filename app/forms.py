from flask.ext.wtf import Form
from wtforms import HiddenField, BooleanField
from wtforms.validators import Required

class LoginForm(Form):
    openid = HiddenField('openid', validators = [Required()], default = "https://www.google.com/accounts/o8/id")
    remember_me = BooleanField('remember_me', default = False)