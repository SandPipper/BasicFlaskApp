import unittest
import time
import hashlib
from app import create_app, db
from datetime import datetime
from app.models import User, Role, AnonymousUser, Permission, Follow

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

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='hard@example.com', password='hard')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))

    def test_timestmaps(self):
        u = User(password='hard')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(password='hard')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email='hard@example.com', password='hard')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
            with self.app.test_request_context('/',
                                               base_url='https://example.com'):
                gravatar_ssl = u.gravatar()
            self.assertTrue('http://www.gravatar.com/avatar/' +
                hashlib.md5(u.email.encode('utf-8')).hexdigest() in gravatar)
            self.assertTrue('s=256' in gravatar_256)
            self.assertTrue('r=pg' in gravatar_pg)
            self.assertTrue('d=retro' in gravatar_retro)
            self.assertTrue('https://secure.gravatar.com/avatar/' +
                hashlib.md5(u.email.encode('utf-8')).hexdigest() in gravatar_ssl)

    def test_follows(self):
        u1 = User(email='hard@example.com', password='hard')
        u2 = User(email='easy@example.org', password='easy')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= timestamp_after)
        f = u2.followers.all()[0]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)
