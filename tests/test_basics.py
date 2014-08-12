import unittest
from flask import current_app
from app import create_app, db
from app.models import User


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_avatar(self):
        u = User(name='raul', email='marvolo@gmail.com')
        avatar = u.avatar(128)
        expected = ('http://www.gravatar.com/avatar/059e89cce0649d6ca4e'
                    'b1f700752422b')
        self.assertTrue(avatar[0:len(expected)] == expected)
