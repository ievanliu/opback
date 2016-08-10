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
from .. import utils, ma
# serializer for JWT
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# exceptions for JWT
from itsdangerous import SignatureExpired, BadSignature, BadData
import datetime
import time


"""
This is a HELPER table for the role_table and user_table to set up
the many-to-many relationship between Role modole and User model.
As Flask official documentation recommanded, this helper table
should not be a model but an actual table.
"""
roles = db.Table(
    'roles',
    db.Column(
        'role_id',
        db.String(64),
        db.ForeignKey('role.role_id')),
    db.Column(
        'user_id',
        db.String(64),
        db.ForeignKey('user.user_id'))
)

"""
This is a HELPER table for the privilege_table and role_table to set up
the many-to-many relationship between Role modole and privilege model.
As Flask official documentation recommanded, this helper table
should not be a model but an actual table.
"""
privileges = db.Table(
    'privileges',
    db.Column(
        'privilege_id',
        db.String(64),
        db.ForeignKey('privilege.privilege_id')),
    db.Column(
        'role_id',
        db.String(64),
        db.ForeignKey('role.role_id'))
)


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
    last_login = db.Column(db.DATETIME)
#    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))
    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('roles', lazy='select'))

#    token = db.relationship(
#        'Token', backref='user', lazy='select')

    def __init__(
            self, userName, hashedPassword, role=None, roleList=None, valid=1):
        self.user_id = utils.genUuid(userName)
        self.user_name = userName
        self.hashed_password = hashedPassword
        self.valid = valid
        # self.role_id = role.role_id
        if roleList:
            self.role = roleList
        if role:
            self.role = [role]
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.user_id

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            app.logger.debug(
                utils.logmsg('save user ' + self.user_name + ' to db.'))
        except Exception, e:
            db.session.rollback()
            msg = self.__DoraemonContraintException % e
            app.logger.info(utils.logmsg(msg))

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

    def addRole(self, roleList=None, role=None):
        if roleList:
            self.roles = roleList
        if role:
            self.roles = [role]
        db.session.commit()
    # def getUserPrivileges(self):
        # self.roles.privileges
#    @staticmethod
#    def getFromUserId(userId):
#        user = User.query.filter_by(user_id=userId, valid=1).first()
#        return user

    """
    token is generated as the JWT protocol.
    JSON Web Tokens(JWT) are an open, industry standard RFC 7519 method
    """
    def genTokenSeq(self, expires):
        s = Serializer(
            secret_key=app.config['SECRET_KEY'],
            salt=app.config['AUTH_SALT'],
            expires_in=expires)
        timestamp = time.time()
        roleIdList = []
        for role in self.roles:
            roleIdList.append(role.role_id)
        return s.dumps(
            {'user_id': self.user_id,
             'user_role': roleIdList,
             'iat': timestamp})
        # The token contains userid, user role and the token generation time.
        # u can add sth more inside, if needed.
        # 'iat' means 'issued at'. claimed in JWT.

    """
    user auth and return user token
    """
    @staticmethod
    def userLogin4token(userName, password):
        user = User.getValidUser(userName=userName)
        if not user:
            msg = 'cannot find user_name:' + userName
            app.logger.debug(msg)
            return [None, None, None, msg]
        elif not userUtils.hash_pass(password) == user.hashed_password:
            msg = 'user name and password cannot match.'
            app.logger.debug(msg)
            return [None, None, None, msg]
        # generate token sequence
        # token expiration time is set in the config file
        # the value is set in seconds: (day,second,microsecond)
        token = user.genTokenSeq(app.config['ACCESS_TOKEN_EXPIRATION'])
#        tokenExp = datetime.datetime.now() + \
#            datetime.timedelta(0, app.config['TOKEN_DURATION'], 0)
#        # generate token obj
#        newToken = Token(tokenId, tokenExp, user.user_id)
        refreshToken = user.genTokenSeq(app.config['REFRESH_TOKEN_EXPIRATION'])
#        # invalid the other tokens of the same user
#        oldTokens = Token.getValidToken(userId=user.user_id)
#        if oldTokens:
#            for i in range(len(oldTokens)):
#                oldTokens[i].valid = 0
#        try:
#            db.session.add(newToken)
#            db.session.commit()
#        except Exception as e:
#            raise utils.InvalidModuleUsage(e)
        msg = 'user (' + userName + ') logged in.'
        # write the login time to db
        user.last_login = datetime.datetime.now()
        user.updateUser()
        app.logger.debug(msg)
        return [token, refreshToken, user, msg]

    @staticmethod
    def tokenAuth(token):
        # token decoding
        s = Serializer(
            secret_key=api.app.config['SECRET_KEY'],
            salt=api.app.config['AUTH_SALT'])
        try:
            data = s.loads(token)
            # token decoding faild
            # if it happend a plenty of times, there might be someone
            # trying to attact your server, so it should be a warning.
        except SignatureExpired:
            msg = 'token expired'
            app.logger.warning(msg)
            return [None, None, msg]
        except BadSignature, e:
            encoded_payload = e.payload
            if encoded_payload is not None:
                try:
                    s.load_payload(encoded_payload)
                except BadData:
                    # the token is tampered.
                    msg = 'token tampered'
                    app.logger.warning(msg)
                    return [None, None, msg]
            msg = 'badSignature of token'
            app.logger.warning(msg)
            return [None, None, msg]
        except:
            msg = 'wrong token with unknown reason'
            app.logger.warning(msg)
            return [None, None, msg]
        if ('user_id' not in data) or ('user_role' not in data):
            msg = 'illegal payload inside'
            app.logger.warning(msg)
            return [None, None, msg]
        msg = 'user(' + data['user_id'] + ') logged in by token.'
#        app.logger.info(msg)
        userId = data['user_id']
        roleId = data['user_role']
        return [userId, roleId, msg]

    @staticmethod
    def tokenRefresh(refreshToken):
        # varify the refreshToken
        [userId, roleIdList, msg] = User.tokenAuth(refreshToken)
        if userId:
            user = User.getValidUser(userId=userId)
            if not user:
                msg = 'cannot find userid'
                app.logger.warning(msg)
                return [None, msg]
        else:
            msg = 'lost userid'
            app.logger.warning(msg)
            return [None, msg]

        if roleIdList:
            for roleId in roleIdList:
                role = Role.getValidRole(roleId=roleId)
                if not role:
                    msg = 'cannot find roleid' + roleId
                    app.logger.warning(msg)
                    return [None, msg]
        else:
            msg = 'lost roleid'
            app.logger.warning(msg)
            return [None, msg]

        token = user.genTokenSeq(app.config['ACCESS_TOKEN_EXPIRATION'])
        msg = "token refreshed"
        return [token, msg]


# class Token(db.Model):
#     """
#     token Model
#     """
#     __tablename__ = 'token'
#     # token_id means tocken sequence
#     token_id = db.Column(db.String(128), primary_key=True)
#     expires = db.Column(db.DATETIME)  # token expire time
#     valid = db.Column(db.SmallInteger)
#     user_id = db.Column(db.String(64), db.ForeignKey('user.user_id'))#

#     def __init__(self, tokenSeq, expires, userId, valid=1):
#         self.token_id = tokenSeq
#         self.expires = expires
#         self.user_id = userId
#         self.valid = valid

#     @staticmethod
#     def getValidToken(userId=None, tokenId=None):
#         if userId and not tokenId:
#             token = Token.query.filter_by(user_id=userId, valid=1).all()
#         elif not userId and tokenId:
#             token = Token.query.filter_by(token_id=tokenId, valid=1).first()
#         elif userId and tokenId:
#             token = Token.query.filter_by(
#                 user_id=userId, token_id=tokenId, valid=1).first()
#         else:
#             token = Token.query.filter_by(valid=1).all()
#         return token

#     @staticmethod
#     def getFromUserId(userId):
#         token = Token.query.filter_by(user_id=userId).all()
#         return token if token else None

#     @staticmethod
#     def getFromTokenId(tokenId):
#         token = Token.query.filter_by(token_id=tokenId).first()
#         return token if token else None


class Role(db.Model):
    """
    role model
    """
    __tablename__ = 'role'
    role_id = db.Column(db.String(64), primary_key=True)
    role_name = db.Column(db.String(64))
    # user = db.relationship('User', backref='role', lazy='dynamic')
    valid = db.Column(db.SmallInteger)
    privileges = db.relationship(
        'Privilege',
        secondary=privileges,
        backref=db.backref('privileges', lazy='select'))
    users = db.relationship(
        'User',
        secondary=roles,
        backref=db.backref('role', lazy='select'))

    def __repr__(self):
        return '<Role %r>' % self.role_id

    def __init__(self, roleName, valid=1):
        self.role_id = utils.genUuid(roleName)
        self.role_name = roleName
        self.valid = valid

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            app.logger.debug(
                utils.logmsg('save role ' + self.role_name + ' to db.'))
        except Exception, e:
            db.session.rollback()
            msg = self.__DoraemonContraintException % e
            app.logger.info(utils.logmsg(msg))

    def addPrivilege(self, privilegeList=None, privilege=None):
        if privilegeList:
            self.privilege = privilegeList
        if privilege:
            self.privilege = [privilege]
        db.session.add(self)
        try:
            db.session.commit()
        except Exception, e:
            db.session.rollback()
            msg = self.__DoraemonContraintException % e
            app.logger.info(utils.logmsg(msg))

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
            role = Role.query.filter_by(valid=1).all()
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
    privilege_id = db.Column(db.String(64), primary_key=True)
    privilege_name = db.Column(db.String(64))
    valid = db.Column(db.SmallInteger)
    roles = db.relationship(
        'Role',
        secondary=privileges,
        backref=db.backref('privilege', lazy='select'))

    def __repr__(self):
        return '<privilege %r>' % self.privilege_id

    def __init__(self, privilegeName, valid=1):
        self.privilege_id = utils.genUuid(privilegeName)
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
        try:
            db.session.commit()
            app.logger.debug(
                utils.logmsg('insert privilege:' + self.privilege_name))
        except Exception, e:
            db.session.rollback()
            msg = self.__DoraemonContraintException % e
            app.logger.info(utils.logmsg(msg))


#####################################################################
#    establish a meta data class for data print                     #
#####################################################################
class UserSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'last_login']

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class RoleSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Role
        fields = ['role_id']

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)


class PrivilegeSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Privilege
        fields = ['privilege_id', 'privilege_name']

privilege_schema = PrivilegeSchema()
privileges_schema = PrivilegeSchema(many=True)
