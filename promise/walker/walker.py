# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Shawn.T
# Email: shawntai.ds@gmail.com
#
# A walker may have one or more trails,
# means an ansible mission work on one or more hosts.
# a shell walker will establish one ansible task with shell module
# a script walker will establish  one ansible task with script module
# a playbook walker will establish  one ansible play with a playbook
#

from flask import g
from flask_restful import reqparse, Resource
from .models import Walker, ShellMission
from . import utils as walkerUtils
# from .. import utils
from ..user import auth


class ShellWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ShellWalkerAPI, self).__init__()

    """
    Establish a shell mission walker, it will return the walker id.
    A walker may have several trails(target hosts).
    """
    @auth.PrivilegeAuth(privilegeRequired="shellExec")
    def post(self):
        # check the arguments
        [ipList, shell, osUser, walkerName] = self.argCheckForPost()

        # setup a walker
        walker = Walker(walkerName)

        [msg, trails] = walker.establish(ipList, g.currentUser)
        # setup a shellmission and link to the walker
        shellMission = ShellMission(shell, osUser, walker)
        shellMission.save()
        walker.save()

        # run the shell mission walker
        [trails, jsonTrails] = shellMission.run()
        msg = 'mission start'
        return {
            'message': msg, 'walker_id': walker.walker_id,
            'trails': jsonTrails}, 200

    """
    find out all the shell-mission walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="shellExec")
    def get(self):
        walkerId = self.argCheckForGet()
        if not walkerId:
            [msg, jsonWalkers] = self.getWalkerListOfTokenOwner()
            return {'message': msg, 'walkers': jsonWalkers}, 200
        else:
            [msg, walker_name, jsonTrails] = self.getWalkerInfoWithinUser(
                walkerId)
            return {
                'message': msg,
                'walker_name': walker_name,
                'trails': jsonTrails}, 200

    """
    arguments check methods
    """
    def argCheckForPost(self):
        self.reqparse.add_argument(
            'iplist', type=list, location='json',
            required=True, help='iplist ip must be a list')
        self.reqparse.add_argument(
            'shell', type=str, location='json',
            required=True, help='shell must be a string')
        self.reqparse.add_argument(
            'osuser', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'name', type=str, location='json',
            help='default walker-name: time-shell')
        args = self.reqparse.parse_args()
        ipList = args['iplist']
        shell = args['shell']
        osUser = args['osuser']
        walkerName = args['name']
        if not walkerName:
            walkerName = str(walkerUtils.serialCurrentTime()) + '-' + shell
        return [ipList, shell, osUser, walkerName]

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'walkerid', type=str,
            location='args', help='walker id must be a string')
        args = self.reqparse.parse_args()
        walkerId = args['walkerid']
        if not walkerId:
            walkerId = None
        return walkerId

    @staticmethod
    def getWalkerListOfTokenOwner():
        [walkers, jsonWalkers] = Walker.getFromUser(g.currentUser)
        msg = 'walker list of ' + g.currentUser.user_name
        return [msg, jsonWalkers]

    @staticmethod
    def getWalkerInfo(walkerId):
        walker = Walker.getFromWalkerId(walkerId)
        if walker:
            [trails, jsonTrails] = Walker.getTrails(walker)
            msg = 'walker info'
        else:
            msg = 'wrong walker id'
        return [msg, walker.walker_name, jsonTrails]

    @staticmethod
    def getWalkerInfoWithinUser(walkerId):
        walker = Walker.getFromWalkerIdWithinUser(walkerId, g.currentUser)
        if walker:
            [trails, jsonTrails] = Walker.getTrails(walker)
            msg = 'walker info'
        else:
            msg = 'wrong walker id'
        return [msg, walker.walker_name, jsonTrails]


class PbWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ShellWalkerAPI, self).__init__()


class ScriptWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ShellWalkerAPI, self).__init__()
