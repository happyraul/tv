import os
from settings import environment
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = environment['SECRET_KEY']
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    TV_MAIL_SUBJECT_PREFIX = '[Snow Day]'
    TV_MAIL_SENDER = 'Snow Day Admin <admin@snow-day.com>'
    TV_ADMIN = environment['SNOW_DAY_ADMIN']
    TVDB_API_KEY = environment['TVDB_API_KEY']
    AWS_BUCKET = environment['AWS_BUCKET']
    AWS_ACCESS_KEY = environment['AWS_ACCESS_KEY']
    AWS_SECRET_KEY = environment['AWS_SECRET_KEY']

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = environment['MAIL_USERNAME']
    MAIL_PASSWORD = environment['MAIL_PASSWORD']
    SQLALCHEMY_DATABASE_URI = ('postgresql://' +
                               environment['DEV_DATABASE_USER'] + ':' +
                               environment['DEV_DATABASE_PASSWORD'] +
                               '@localhost/tv_dev')


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = ('postgresql://' +
                               environment['TEST_DATABASE_USER'] + ':' +
                               environment['TEST_DATABASE_PASSWORD'] +
                               '@localhost/tv_test')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = ('postgresql://' + environment['DATABASE_USER'] +
                               ':' + environment['DATABASE_PASSWORD'] +
                               '@localhost/tv')

config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

#CSRF_ENABLED = True

# OPENID_PROVIDERS = [
#     { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
#     { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#     { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#     { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#     { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
