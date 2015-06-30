
import sys
sys.path.append('src')
sys.path.append('.')

from flask.ext.script import Manager, Shell
from tecstack.app import app, db
from flask.ext.migrate import Migrate, MigrateCommand

import tecstack.models

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def initdb():
    import os
    if not os.path.exists(app.config['DB_FOLDER']):
        os.mkdir(app.config['DB_FOLDER'])
    db.create_all()
    print 'Database inited, location: ' + app.config['SQLALCHEMY_DATABASE_URI']

@manager.command
def dropdb():
    db.drop_all()
    print 'Database droped.'


def _make_context():
    return dict(app=app, db=db, models=tecstack.models)

manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
