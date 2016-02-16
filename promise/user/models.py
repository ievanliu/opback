# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the model module for the user package
# holding user, token, role and  privilege models, etc.
#
from .. import db, api, app
from . import utils as userUtils
from .. import utils
from itsdangerous import JSONWebSignatureSerializer as Serializer
import datetime
import time


class User(db.Model):
    """
    User model
    For the sake of Operation Audit, u shouldn't delete any user.
    Instead, u can set user into 'invalid' status. so I privide the
    'setInvalid()' method to do this.
    """
    __tablename__ = 'user'
    # user_id is a 64Byte UUID depend on the timestamp, namespace and username
    user_id = db.Column(db.String(64), primary_key=True)
    user_name = db.Column(db.String(128))
    hashed_password = db.Column(db.String(128))
    valid = db.Column(db.SmallInteger)
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))
    token = db.relationship(
        'Token', backref='user', lazy='select')

    def __init__(self, userName, hashedPassword, role, valid=1):
        self.user_id = utils.genUuid(userName)
        self.user_name = userName
        self.hashed_password = hashedPassword
        self.valid = valid
        self.role_id = role.role_id

    def __repr__(self):
        return '<User %r>' % self.user_id

    @staticmethod
    def getValidUser(userName=None, userId=None):
        if userName and not userId:
            user = User.query.filter_by(user_name=userName, valid=1).first()
        elif not userName and userId:
            user = User.query.filter_by(user_id=userId, valid=1).first()
        elif userName and userId:
            user = User.query.filter_by(
                user_id=userId, userName=userName).first()
        else:
            user = User.query.filter_by(valid=1).all()
        return user

    def setInvalid(self):
        self.valid = 0
        db.session.commit()
        app.logger.debug(utils.logmsg('set invalid user:' + self.user_name))

    def insertUser(self):
        db.session.add(self)
        db.session.commit()
        app.logger.debug(utils.logmsg('insert new user:' + self.user_name))

    def updateUser(self):
        db.session.commit()
        app.logger.debug(utils.logmsg(
            'user info change user:' + self.user_name))

#    @staticmethod
#    def getFromUserId(userId):
#        user = User.query.filter_by(user_id=userId, valid=1).first()
#        return user

    """
    token is generated as the JWT protocol.
    JSON Web Tokens(JWT) are an open, industry standard RFC 7519 method
    """
    def genTokenSeq(self):
        s = Serializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['AUTH_SALT'])
        timestamp = time.time()
        return s.dumps(
            {'user_id': self.user_id,
             'user_role': self.role_id,
             'timestamp': timestamp})
        # The token contains userid, user role and the token generation time.
        # u can add sth more, if needed.

    """
    user auth and return user token
    """
    @staticmethod
    def userLogin4token(userName, password):
        user = User.getValidUser(userName=userName)
        if not user:
            msg = 'cannot find user_name:'+userName
            app.logger.debug(msg)
            return [None, None, None, msg]
        elif not userUtils.hash_pass(password) == user.hashed_password:
            msg = 'user name and password cannot match.'
            app.logger.debug(msg)
            return [None, None, None, msg]
        # generate token sequence
        tokenId = user.genTokenSeq()
        # set the token expiration time by the config file
        # the value is set in seconds: (day,second,microsecond)
        tokenExp = datetime.datetime.now() + \
            datetime.timedelta(0, app.config['TOKEN_DURATION'], 0)
        # generate token obj
        newToken = Token(tokenId, tokenExp, user.user_id)
        refreshToken = 'refresh Token'
        # invalid the other tokens of the same user
        oldTokens = Token.getValidToken(userId=user.user_id)
        if oldTokens:
            for i in range(len(oldTokens)):
                oldTokens[i].valid = 0
        try:
            db.session.add(newToken)
            db.session.commit()
        except Exception as e:
            raise utils.InvalidModuleUsage(e)
        msg = 'user ('+userName+') logged in.'
        app.logger.debug(msg)
        return [newToken, refreshToken, user, msg]


class Token(db.Model):
    """
    token Model
    """
    __tablename__ = 'token'
    # token_id means tocken sequence
    token_id = db.Column(db.String(128), primary_key=True)
    expires = db.Column(db.DATETIME)  # token expire time
    valid = db.Column(db.SmallInteger)
    user_id = db.Column(db.String(64), db.ForeignKey('user.user_id'))

    def __init__(self, tokenSeq, expires, userId, valid=1):
        self.token_id = tokenSeq
        self.expires = expires
        self.user_id = userId
        self.valid = valid

    @staticmethod
    def getValidToken(userId=None, tokenId=None):
        if userId and not tokenId:
            token = Token.query.filter_by(user_id=userId, valid=1).all()
        elif not userId and tokenId:
            token = Token.query.filter_by(token_id=tokenId, valid=1).first()
        elif userId and tokenId:
            token = Token.query.filter_by(
                user_id=userId, token_id=tokenId, valid=1).first()
        else:
            token = Token.query.filter_by(valid=1).all()
        return token

#    @staticmethod
#    def getFromUserId(userId):
#        token = Token.query.filter_by(user_id=userId).all()
#        return token if token else None

#    @staticmethod
#    def getFromTokenId(tokenId):
#        token = Token.query.filter_by(token_id=tokenId).first()
#        return token if token else None

    @staticmethod
    def tokenAuth(tokenId):
        # token decoding
        s = Serializer(
            secret_key=api.app.config['SECRET_KEY'],
            salt=api.app.config['AUTH_SALT'])
        try:
            data = s.loads(tokenId)
        except:
            # token decoding faild
            # if it happend a plenty of times, there might be someone
            # trying to attact your server, so i set it as 'warning'level.
            msg = 'illegal token series'
            app.logger.warning(msg)
            return [None, msg]
        if 'user_id' not in data:
            # token with wrong data inside
            # if it happend a plenty of times, there might be someone
            # trying to attact your server, so i set it as 'warning'level.
            msg = 'illegal token data inside'
            app.logger.warning(msg)
            return [None, msg]
        # check token to the db
        strDatetimeNow = str(datetime.datetime.now())
        token = Token.query.filter(
            Token.token_id == tokenId,
            Token.valid == 1, Token.user_id == data['user_id'],
            Token.expires > strDatetimeNow).first()
        if not token:
            # token invalid or expired
            msg = 'token invalid or expired'
            app.logger.info(msg)
            return [None, msg]

        user = token.user
        # expand the expire time
        token.expires = datetime.datetime.now() + \
            datetime.timedelta(0, app.config['TOKEN_DURATION'], 0)
        db.session.commit()
        msg = 'user('+user.user_name+') logged in by token.'
        app.logger.info(msg)
        return [user, msg]

"""
This is a HELPER table for the privilege_table and role_table to set up
the many-to-many relationship between Role modole and privilege model.
As Flask official document recommanded, this helper table
should not be a model but an actual table.
"""
privileges = db.Table(
    'privileges',
    db.Column(
        'privilege_id',
        db.Integer,
        db.ForeignKey('privilege.privilege_id')),
    db.Column(
        'role_id',
        db.Integer,
        db.ForeignKey('role.role_id'))
    )


class Role(db.Model):
    """
    role model
    """
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(64))
    user = db.relationship('User', backref='role', lazy='dynamic')
    valid = db.Column(db.SmallInteger)
    privileges = db.relationship(
        'Privilege',
        secondary=privileges,
        backref=db.backref('privileges', lazy='select'))

    def __repr__(self):
        return '<Role %r>' % self.role_id

    def __init__(self, roleName, valid=1):
        self.role_name = roleName
        self.valid = valid

    def addPrivilege(self, privilegeList=None, privilege=None):
        if privilegeList:
            self.privilege = privilegeList
        if privilege:
            self.privilege = [privilege]
        db.session.commit()

    @staticmethod
    def getValidRole(roleName=None, roleId=None):
        if roleName and not roleId:
            role = Role.query.filter_by(role_name=roleName, valid=1).first()
        elif not roleName and roleId:
            role = Role.query.filter_by(role_id=roleId, valid=1).first()
        elif roleName and roleId:
            role = Role.query.filter_by(
                role_id=roleId, role_name=roleName, valid=1).first()
        else:
            role = role = Role.query.filter_by(valid=1).all()
        return role

#    @staticmethod
#    def getFromRoleName(roleName):
#        role = Role.query.filter_by(role_name=roleName).first()
#        return role

    def setInvalid(self):
        self.valid = 0
        db.session.commit()

    @staticmethod
    def deleteFromRoleName(roleName):
        role = Role.getValidRole(roleName)
        if role:
            # deal with the dependence with other tables:
            # Privilege, User have a foriegn key of role_id
            role.privileges = []
            role.users = []

            role.valid = 0
            db.session.commit()

            msg = 'invalid role(' + roleName + ')'
            app.logger.debug(utils.logmsg(msg))
            return True
        msg = 'cannot find role(' + roleName + ')'
        app.logger.debug(utils.logmsg(msg))
        return False


class Privilege(db.Model):
    """
    privilege model
    """
    __tablename__ = 'privilege'
    privilege_id = db.Column(db.Integer, primary_key=True)
    privilege_name = db.Column(db.String(64))
    valid = db.Column(db.SmallInteger)
    roles = db.relationship(
        'Role',
        secondary=privileges,
        backref=db.backref('privilege', lazy='select'))

    def __repr__(self):
        return '<privilege %r>' % self.privilege_id

    def __init__(self, privilegeName, valid=1):
        self.privilege_name = privilegeName
        self.valid = valid

    @staticmethod
    def getValidPrivilege(privilegeId=None, privilegeName=None):
        if privilegeId and not privilegeName:
            privilege = Privilege.query.filter_by(
                privilege_id=privilegeId, valid=1).first()
        elif not privilegeId and privilegeName:
            privilege = Privilege.query.filter_by(
                privilege_name=privilegeName, valid=1).first()
        elif privilegeId and privilegeName:
            privilege = Privilege.query.filter_by(
                privilege_id=privilegeId,
                privilege_name=privilegeName,
                valid=1).first()
        else:
            privilege = Privilege.query.filter_by(valid=1).all()
        return privilege

    @staticmethod
    def getFromPrivilegeName(privilegeName):
        privilege = Privilege.query.filter_by(
            privilege_name=privilegeName).first()
        return privilege

    def insertPrivilege(self):
        db.session.add(self)
        db.session.commit()
        app.logger.debug(
            utils.logmsg('insert privilege:' + self.privilege_name))
