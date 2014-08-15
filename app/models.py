from app import db
from flask.ext.login import UserMixin
from . import login_manager
from hashlib import md5


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', cascade="all,delete")

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)

    def upcoming(self):
        return [
            {
                'air_date': 'April 18, 2014',
                'series': {'name': 'Game of Thrones'},
                'name': 'Song of Ice and Fire',
            },
            {
                'air_date': 'September 11, 2014',
                'series': {'name': 'Breaking Bad'},
                'name': 'Felina',
            },
            {
                'air_date': 'December 7, 2014',
                'series': {'name': 'Star Trek: The Next Generation'},
                'name': 'Inner Light',
            },
        ]

    def avatar(self, size):
        return ('http://www.gravatar.com/avatar/' +
                md5(self.email).hexdigest() + '?d=mm&s=' + str(size))

    def __repr__(self):
        return '<User %r>' % (self.name)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
