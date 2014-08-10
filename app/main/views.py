from flask import render_template, redirect, flash, url_for
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditForm
from .. import db
#from ..models import User

# @main.route('/', methods=['GET', 'POST'])
# @main.route('/index', methods=['GET', 'POST'])
# @login_required
# def index():
#     posts = [ # fake array of posts
#         {
#             'author': { 'nickname': 'John' },
#             'body': 'Beautiful day in Portland!'
#         },
#         {
#             'author': { 'nickname': 'Susan' },
#             'body': 'The Avengers movie was so cool!'
#         }
#     ]
#     return render_template("index.html", title='Home', user=current_user, posts=posts)

@main.route('/')
@login_required
def user():
    if current_user == None:
        flash('Must be logged in to see this page.')
        return redirect(url_for('auth.login'))
    return render_template('user.html',
        user=current_user,
        favorites=[])
    
@main.route('/profile')
@login_required
def profile():
    if current_user == None:
        flash('Must be logged in to see this page.')
        return redirect(url_for('auth.login'))
    return render_template('profile.html', user=current_user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('.profile'))
    else:
        form.name.data = current_user.name
    return render_template('edit-profile.html', user=current_user, form=form)
