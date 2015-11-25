# -*- coding:utf-8 -*-
import sys
sys.path.append('.')

from flask.ext.script import Manager, Shell, prompt_bool
from flask.ext.migrate import Migrate, MigrateCommand

from promise import app, db
from promise.user import utils as userUtils
from promise.user.models import User, Privilege, Role

migrate = Migrate(app, db)

manager = Manager(app, usage="Perform database operations")

manager.add_command('db', MigrateCommand)


@manager.command
def initdb():
    "initialize database tables"
    import os
    if not os.path.exists(app.config['DB_FOLDER']):
        os.mkdir(app.config['DB_FOLDER'])
    db.create_all()
    print 'Database inited, location: ' + app.config['SQLALCHEMY_DATABASE_URI']


@manager.command
def importdata():
    "Import data into database tables"

    # init privileges
    privilegeNameList = ['userAdmin', 'inventoryAdmin']
    privilegeList = []
    for item in privilegeNameList:
        newPrivilege = Privilege(item)
        db.session.add(newPrivilege)
        privilegeList.append(newPrivilege)

    # init roles
    roleRoot = Role('root')
    roleRoot.addPrivilege(privilegeList=privilegeList)
    roleOperator = Role('operator')
    roleInventoryAdmin = Role('InventoryAdmin')
    roleInventoryAdmin.addPrivilege(privilege=newPrivilege)
    db.session.add(roleRoot)
    db.session.add(roleOperator)
    db.session.add(roleInventoryAdmin)
    db.session.commit()  # commit the roles before user init

    # init users
    user1 = User('tom', userUtils.hash_pass("tompass"), roleOperator)
    user2 = User(
        'jerry', userUtils.hash_pass("jerrypass"), roleInventoryAdmin)
    rootUser = User(
        app.config['DEFAULT_ROOT_USER_NAME'],
        userUtils.hash_pass(app.config['DEFAULT_ROOT_PASSWORD']),
        roleRoot)
    visitor = User('visitor', 'visitor', roleOperator)

    db.session.add(rootUser)
    db.session.add(visitor)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    print 'Data imported'


@manager.command
def dropdb():

    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Database droped.'


@manager.command
def recreatedb():
    "Recreates database tables \
    (same as issuing 'drop', 'create' and then 'import')"
    dropdb()
    initdb()
    importdata()


def _make_context():
    return dict(app=app, db=db)

manager.add_command("shell", Shell(make_context=_make_context))


if __name__ == '__main__':
    manager.run()
