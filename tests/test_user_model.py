import unittest
import time
from app import create_app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password = 'hard')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password = 'hard')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'hard')
        self.assertTrue(u.verify_password('hard'))
        self.assertFalse(u.verify_password('easy'))

    def test_password_salts_are_random(self):
        u = User(password = 'hard')
        u2 = User(password = 'hard')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='hard')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='hard')
        u2 = User(password='easy')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password='hard')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='easy')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'hard'))
        self.assertTrue(u.verify_password('hard'))

    def test_invalid_reset_token(self):
        u1 = User(password='easy')
        u2 = User(password='hard')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, 'middle'))
        self.assertTrue(u2.verify_password('hard'))

    def test_valid_email_change_token(self):
        u = User(email='hard@example.com', password='hard')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('easy@example.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'easy@example.com')

    def test_invalid_email_change_token(self):
        u1 = User(email='hard@example.com', password='hard')
        u2 = User(email='easy@example.com', password='easy')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('middle@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'easy@example.com')

    def test_duplicate_email_change_token(self):
        u1 = User(email='hard@example.com', password='hard')
        u2 = User(email='easy@example.com', password='easy')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('hard@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'easy@example.com')
