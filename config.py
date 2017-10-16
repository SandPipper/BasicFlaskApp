import os
import datetime


class Auth:
    CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
    CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
    REDIRECT_URI = 'http://localhost:5000/auth/login_auth'
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    SCOPE = ['profile', 'email']


class Config:

    SECRET_KEY = os.environ['SECRET_KEY']
    BLOG_MAIL_SUBJECT_PREFIX = '[My Blog]'
    BLOG_ADMIN = os.environ['BLOG_ADMIN']
    BLOG_MAIL_SENDER = 'My Blog Admin {}'.format(BLOG_ADMIN)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@localhost/?charset=utf8mb4'\
                               .format(os.environ['DB_USERNAME'],
                                       os.environ['DB_PASSWORD'])
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REMEMBER_COOKIE_DURATION = datetime.timedelta(days=30)
    BLOG_POSTS_PER_PAGE = 20
    BLOG_FOLLOWERS_PER_PAGE = 50
    BLOG_COMMENTS_PER_PAGE = 30


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    DB_NAME = os.environ['DEV_DB_NAME']


class TestingConfig(Config):

    TESTING = True
    DB_NAME = os.environ['TEST_DB_NAME']


class ProductionConfig(Config):

    DB_NAME = os.environ['PROD_DB_NAME']


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
