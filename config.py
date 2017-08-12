import os


class Config:

    SECRET_KEY = os.environ['SECRET_KEY']
    BLOG_MAIL_SUBJECT_PREFIX = '[My Blog]'
    BLOG_ADMIN = os.environ['BLOG_ADMIN']
    BLOG_MAIL_SENDER = 'My Blog Admin {}'.format(BLOG_ADMIN)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@localhost/?charset=utf8mb4'\
                               .format(os.environ['DB_USERNAME'],
                                       os.environ['DB_PASSWORD'])
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    BLOG_POSTS_PER_PAGE = 20
    BLOG_FOLLOWERS_PER_PAGE = 50


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
