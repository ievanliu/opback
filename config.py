# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
# This is the config file of global package of promise.

import os
basedir = os.path.abspath(os.path.dirname('..'))

"""
    database configuration
"""
# database access string setting, by default we use mysql
SQLALCHEMY_DATABASE_URI = 'mysql://dbname:dbpassword@ip:port/dbname'
# when testing, put your instance setting in instance/config.py to cover it
# SQLALCHEMY_DATABASE_URI = 'mysql://root:111111@192.168.182.50:3306/dev4test'

# ADVISE：create instance/config.py, your sqlite setting might like this:
# get some folders and dirs:
# import os
basedir = os.path.abspath(os.path.dirname('..'))
DB_FOLDER = os.path.join(basedir,  '.data')
DB_FILE = 'app.db'
DB_SOURCEFILE = 'data.sql'
DB_FILEPATH = os.path.join(DB_FOLDER, DB_FILE)
DB_SOURCEFILEPATH = os.path.join(DB_FOLDER, DB_SOURCEFILE)
# config the sqlite acces URI:
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DB_FOLDER, DB_FILE)


"""
    log file configuration
"""
LOGGER_FOLDER = os.path.join(basedir,  '.log')
LOGGER_FILE = os.path.join(LOGGER_FOLDER, 'debug.log')

"""
    encryption & auth configuration
"""
# encryption keys
SECRET_KEY = 'your SECRET_KEY'
# salt used by token generation
AUTH_SALT = 'your AUTH SALT'
# salt used by password md5 hash
PSW_SALT = 'your PSW SALT'
# token duration (in seconds), 2hours by default
TOKEN_DURATION = 7200  # in second
ACCESS_TOKEN_EXPIRATION = 3600  # in second
REFRESH_TOKEN_EXPIRATION = 86400  # in second
# root user default setting
DEFAULT_ROOT_USER_NAME = 'admin'
DEFAULT_ROOT_PASSWORD = 'admin'
