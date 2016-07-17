# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# This is the model module for the walker package
# holding walker, trail.. etc.
#
from .. import db, app
# from . import utils as walkerUtils
from .. import utils, ma


class Walker(db.Model):
    """
    shellWalker model
    """
    __tablename__ = 'walker'
    walker_id = db.Column(db.String(64), primary_key=True)
    walker_name = db.Column(db.String(64))
    # shell = db.Column(db.string(256))
    # iplist = db.Column(db.String(2560))
    valid = db.Column(db.SmallInteger)
    # all the trails of this wallker
    trails = db.relationship('Trail', backref='walker', lazy='dynamic')
    shellmissions = db.relationship(
        'ShellMission', backref='walker', lazy='dynamic')
    # owner of this walker
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    # state code:
    # Null: has no state yet
    # -2: established
    # -1: running
    #  0: all success
    # >0: num of faild tasks
    state = db.Column(db.Integer)

    def __repr__(self):
        return '<walker %r>' % self.walker_id

    def __init__(self, walker_name, valid=1):
        self.walker_id = utils.genUuid(walker_name)
        self.walker_name = walker_name
        self.valid = valid

    def save(self):
        db.session.add(self)
        db.session.commit()
        app.logger.debug(
            utils.logmsg('save walker ' + self.walker_name + ' to db.'))

    def establish(self, iplist, owner):
        '''
        establish the walker
        '''
        self.owner_id = owner.user_id
        self.state = -1
        # establish trails(one target ip with one trail)
        trailList = []
        for ip in iplist:
            trail = Trail(ip)
            trail.insertTrail()
            trailList.append(trail)

        [msg, state] = self.addTrailList(trailList)
        if state is not 0:
            return [msg, None]
#                msg = 'walker' + self.walker_id + ' establish faild.'
#                app.logger.warning(utils.logmsg(msg))
#                return [msg, None]
        self.save()
        msg = 'walker' + self.walker_id + ' established'
        app.logger.debug(utils.logmsg(msg))
        return [msg, self.trails.all()]

    def addTrailList(self, trailList):
        self.trails = trailList
        try:
            db.session.add(self)
            db.session.commit()
        except:
            msg = 'add trail faild.'
            app.logger.debug(utils.logmsg(msg))
            return [msg, 1]
        msg = 'add trails success.'
        app.logger.debug(utils.logmsg(msg))
        return [msg, 0]

    def getTrails(self):
        return self.trails.all()

    @staticmethod
    def getFromUser(user):
        print user.user_id
        walkers = Walker.query.filter_by(owner_id=user.user_id).all()
        print walkers
        jsonWalkers = walkers_schema.dump(walkers).data
        return [walkers, jsonWalkers]


class ShellMission(db.Model):
    """
    shellWalker model
    """
    __tablename__ = 'shellmission'
    shellmission_id = db.Column(db.String(64), primary_key=True)
    shell = db.Column(db.String(256))
    # run the shell as this user on the target hosts
    osuser = db.Column(db.String(64))
    walker_id = db.Column(db.Integer, db.ForeignKey('walker.walker_id'))
    # walker = db.relationship()

    def __repr__(self):
        return '<shellmission %r>' % self.shellmission_id

    def __init__(self, shell, osuser, walker):
        self.shellmission_id = utils.genUuid(shell)
        self.shell = shell
        self.osuser = osuser
        self.walker_id = walker.walker_id

    def save(self):
        db.session.add(self)
        db.session.commit()
        app.logger.debug(
            utils.logmsg('save shell mission:' + self.shellmission_id))

    def getTrails(self):
        return self.walker.getTrails()

    def run(self):
        trails = self.getTrails()
        jsonTrails = trails_schema.dump(trails).data
        return [trails, jsonTrails]


class Trail(db.Model):
    '''
    a trail stores the result of task running on ONE host
    '''
    __tablename__ = 'trail'
    trail_id = db.Column(db.String(64), primary_key=True)
    ip = db.Column(db.String(15))
    stdout = db.Column(db.Text)
    state = db.Column(db.Integer)
    # state code:
    # Null: has no state yet
    # -2: established
    # -1: running
    #  0: all success
    # >0: num of faild tasks
    walker_id = db.Column(db.Integer, db.ForeignKey('walker.walker_id'))

    def __repr__(self):
        return '<trail %r>' % self.trail_id

    def __init__(self, ip, stdout=None, state=-2):
        self.trail_id = utils.genUuid(str(ip))
        self.ip = ip
        self.stdout = stdout
        self.state = state

    def insertTrail(self):
        db.session.add(self)
        db.session.commit()
        app.logger.debug(utils.logmsg('insert new trail:' + self.trail_id))


#####################################################################
#    establish a meta data class for data print                     #
#####################################################################
class WalkerSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Walker
        fields = ['walker_id', 'walker_name']
walker_schema = WalkerSchema()
walkers_schema = WalkerSchema(many=True)


class TrailSchema(ma.HyperlinkModelSchema):
    """
        establish a meta data class for data print
    """
    class Meta:
        model = Trail
        fields = ['trail_id']
trail_schema = TrailSchema()
trails_schema = TrailSchema(many=True)
