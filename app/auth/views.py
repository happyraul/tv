from flask import render_template, flash, redirect, url_for, request, session
from flask.ext.login import login_user, logout_user, login_required,\
    current_user
from . import auth
from ..models import User
from .forms import LoginForm
from .. import oid, db
from datetime import datetime

ROLE_USER = 2


@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()


@auth.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if current_user.is_authenticated():
        return redirect(url_for('main.user'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        # flash('Login requested for OpenID="' + form.openid.data +
        #     '", remember_me=' + str(form.remember_me.data))
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
        #return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('auth/login.html', title='Sign In', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.user'))


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('.login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        name = resp.nickname
        if name is None or name == "":
            name = resp.email.split('@')[0]
        user = User(name=name, email=resp.email, role_id=ROLE_USER,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('main.user'))
