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
from .models import Walker
from . import utils as walkerUtils
from .. import utils
from ..user import auth


class WalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(WalkerAPI, self).__init__()

    """
    find out all the walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="walkerInfo")
    def get(self):
        walker_id = self.argCheckForGet()
        if not walker_id:
            [msg, json_walkers] = self.getWalkerListOfTokenOwner()
            return {'message': msg, 'walkers': json_walkers}, 200
        else:
            [msg, walker_name, json_trails] = self.getWalkerInfoWithinUser(
                walker_id)
            return {
                'message': msg,
                'walker_name': walker_name,
                'trails': json_trails}, 200

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
        iplist = args['iplist']
        for ip in iplist:
            if not walkerUtils.ipFormatChk(ip):
                msg = 'wrong ip address'
                raise utils.InvalidAPIUsage(msg)
        shell = args['shell']
        os_user = args['osuser']
        walker_name = args['name']
        if not walker_name:
            walker_name = str(walkerUtils.serialCurrentTime()) + '-' + shell
        return [iplist, shell, os_user, walker_name]

    def argCheckForGet(self):
        self.reqparse.add_argument(
            'walkerid', type=str,
            location='args', help='walker id must be a string')
        args = self.reqparse.parse_args()
        walker_id = args['walkerid']
        if not walker_id:
            walker_id = None
        return walker_id

    @staticmethod
    def getWalkerListOfTokenOwner():
        [walkers, json_walkers] = Walker.getFromUser(g.currentUser)
        msg = 'walker list of ' + g.currentUser.user_name
        return [msg, json_walkers]

    @staticmethod
    def getWalkerInfoWithinUser(walker_id):
        [walker, json_walker] = Walker.getFromWalkerIdWithinUser(
            walker_id, g.currentUser)
        if walker:
            [trails, json_trails] = Walker.getTrails(walker)
            msg = 'walker info'
        else:
            msg = 'wrong walker id'
        return [msg, walker.walker_name, json_trails]
