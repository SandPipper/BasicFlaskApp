from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_pagedown import PageDown
import os

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from sqlalchemy import create_engine
    query_cache = {}
    mysql_engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'],
                   execution_options={'compiled_cache': query_cache})
    mysql_engine.execute('CREATE DATABASE IF NOT EXISTS {}\
                         CHARACTER SET utf8 COLLATE utf8_unicode_ci'\
                         .format(app.config['DB_NAME']))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@localhost/{}?charset=utf8mb4'\
                               .format(os.environ['DB_USERNAME'],
                                       os.environ['DB_PASSWORD'],
                                       app.config['DB_NAME'])


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
