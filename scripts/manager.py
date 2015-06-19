
import sys
sys.path.append('src')

from flask.ext.script import Manager
from tecstack.app import app

manager = Manager(app)


@manager.command
def hello():
    print 'Hello'


if __name__ == '__main__':
    manager.run()
