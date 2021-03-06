from app import db
from flask import current_app
from flask.ext.login import UserMixin
from . import login_manager
from hashlib import md5
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import random
import os
import requests

IMAGE_TYPES = ['poster', 'series', 'fanart', 'season']

STATUSES = {'Continuing': 'c', 'Ended': 'e', 'On Hiatus': 'h', 'Other': 'o'}
# Add inverse mapping
STATUSES.update(dict((STATUSES[k], k) for k in STATUSES))

DAYS_OF_WEEK = {'Sunday': 'su',
                'Monday': 'mo',
                'Tuesday': 'tu',
                'Wednesday': 'we',
                'Thursday': 'th',
                'Friday': 'fr',
                'Saturday': 'sa'}
# Add inverse mapping
DAYS_OF_WEEK.update(dict((DAYS_OF_WEEK[k], k) for k in DAYS_OF_WEEK))

user_images = db.Table('user_images',
                       db.Column('user_id', db.Integer,
                                 db.ForeignKey('users.id'), nullable=False),
                       db.Column('image_id', db.Integer,
                                 db.ForeignKey('images.id'), nullable=False))

user_series = db.Table('user_series',
                       db.Column('user_id', db.Integer,
                                 db.ForeignKey('users.id'), nullable=False),
                       db.Column('series_id', db.Integer,
                                 db.ForeignKey('series.id'), nullable=False))


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
    images = db.relationship('Image', secondary=user_images, lazy='dynamic')
    favorites = db.relationship('Series', secondary=user_series,
                                lazy='dynamic')
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)

    def save_images(self, series):
        for image in series.images:
            self.images.append(image)
            db.session.merge(self)
            db.session.commit()

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


class Series(db.Model):
    __tablename__ = 'series'
    id = db.Column(db.Integer, primary_key=True)
    air_day = db.Column(db.Enum('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa',
                        name='day_of_week'))
    air_time = db.Column(db.Time)
    first_aired = db.Column(db.Date)
    network = db.Column(db.String())
    overview = db.Column(db.String())
    rating = db.Column(db.Numeric(3, 1))
    rating_count = db.Column(db.Integer)
    runtime = db.Column(db.Integer)
    name = db.Column(db.String(), nullable=False)
    status = db.Column(db.Enum('c', 'e', 'h', 'o', name='status'))
    last_updated = db.Column(db.DateTime)
    episodes = db.relationship('Episode', backref='series', lazy='dynamic')
    images = db.relationship('Image', backref='series', lazy='dynamic')

    def __repr__(self):
        return '<Series %r>' % (self.name)

    def __unicode__(self):
        return '<Series %r>' % (self.name)

    def image(self, type, user):
        images = self.all_images(type, user)
        return (random.choice(images) if images else "")

    def all_images(self, type, user):
        if self in user.favorites.all():
            return user.images.filter_by(series=self, type=type).all()
        else:
            return self.images.filter_by(type=type, episode=None).all()


class Episode(db.Model):
    __tablename__ = 'episodes'
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'),
                          nullable=False)
    season = db.Column(db.Integer)
    episode_number = db.Column(db.Integer)
    name = db.Column(db.String())
    overview = db.Column(db.String())
    rating = db.Column(db.Numeric(3, 1))
    rating_count = db.Column(db.Integer)
    air_date = db.Column(db.Date)
    images = db.relationship('Image', backref='episode', lazy='dynamic')

    def __repr__(self):
        return '<Episode %r>' % (self.name)

    def __unicode__(self):
        return '<Episode %r>' % (self.name)

    def image(self, user):
        return (random.choice(self.images.all()) if self.images.all() else "")


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    episode_id = db.Column(db.Integer, db.ForeignKey('episodes.id'),
                           nullable=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'),
                          nullable=False)
    source = db.Column(db.String, nullable=False, unique=True)
    key = db.Column(db.String, nullable=False, unique=True)
    type = db.Column(db.Enum('poster', 'series', 'fanart', 'season',
                     name='image_types'), nullable=False)

    def save(self):
        conn = S3Connection(current_app.config['AWS_ACCESS_KEY'],
                            current_app.config['AWS_SECRET_KEY'])
        bucket = conn.get_bucket(current_app.config['AWS_BUCKET'],
                                 validate=False)
        key = Key(bucket, self.key)

        if not key.exists():
            current_app.logger.debug("Saving image: %s" % self.source)

            r = requests.get(self.source)
            if r.status_code == 200:
                key.set_contents_from_string(r.content)

        else:
            current_app.logger.debug("Image: %s already saved." % self.key)

    def get_url(self):
        conn = S3Connection(current_app.config['AWS_ACCESS_KEY'],
                            current_app.config['AWS_SECRET_KEY'])
        bucket = conn.get_bucket(current_app.config['AWS_BUCKET'],
                                 validate=False)
        key = Key(bucket, self.key)
        return key.generate_url(600)

    def __repr__(self):
        return '<Image %r>' % (self.key)

    def __unicode__(self):
        return '<Image %r>' % (self.key)
