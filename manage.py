#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment, \
                       Vote_comment, Vote_post, Favorites_post
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.environ['FLASK_CONFIG'])
manager = Manager(app)
migrate = Migrate(app, db)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Follow=Follow,
                Permission=Permission, Post=Post, Comment=Comment,
                Vote_comment=Vote_comment, Vote_post=Vote_post,
                Favorites_post=Favorites_post)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
