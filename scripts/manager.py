
import sys
sys.path.append('.')

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
'''
    add by daisheng
'''
from sqlite3 import dbapi2 as sqlite3

from tecstack import app, db
from tecstack import auth
'''
    add by Leann Mak 2015/7/5
'''
from tecstack import vminfo
'''
    end
'''

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

'''
    add by Shawn.T
'''


@manager.command
def importdata():
    rv = sqlite3.connect(app.config['DB_FILEPATH'])
    rv.row_factory = sqlite3.Row
    with app.open_resource(app.config['DB_SOURCEFILEPATH'], mode='r') as f:
        rv.cursor().executescript(f.read())
    rv.commit()
    '''
        add by Leann Mak 2015/7/5
    '''
    rv.close()
    '''
        end
    '''
    print 'vminfo Data imported, source file: ' \
          + app.config['DB_SOURCEFILEPATH']


@manager.command
def dropdb():
    db.drop_all()
    print 'Database droped.'


def _make_context():
    return dict(app=app, db=db, auth=auth, vminfo=vminfo)

manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
