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
from .. import app
from ..ansiAdapter.ansiAdapter import ShellExecAdapter
from .. import utils
from ..user import auth
import thread


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
        [iplist, shell, os_user, walker_name] = self.argCheckForPost()

        # setup a walker
        walker = Walker(walker_name)

        [msg, trails] = walker.establish(iplist, g.currentUser)
        # setup a shellmission and link to the walker
        shell_mission = ShellMission(shell, os_user, walker)
        shell_mission.save()
        walker.save()

        # setup a shell mission walker executor
        shell_walker_executor = ShellWalkerExecutor(shell_mission)

        if shell_walker_executor:
            # run the executor
            thread.start_new_thread(shell_walker_executor.run, ())
            # shell_walker_executor.run()

        [trails, json_trails] = walker.getTrails()

        msg = 'mission start'
        return {
            'message': msg, 'walker_id': walker.walker_id,
            'trails': json_trails}, 200

    """
    find out all the shell-mission walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="shellExec")
    def get(self):
        walker_id = self.argCheckForGet()
        if not walker_id:
            [msg, json_walkers] = self.getWalkerListOfTokenOwner()
            return {'message': msg, 'walkers': json_walkers}, 200
        else:
            [msg, walker_name, json_trails] = self.getWalkerInfoOfTokenOwner(
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
        [walkers, json_walkers] = Walker.getShellMissionWalker(g.currentUser)
        msg = 'walker list of ' + g.currentUser.user_name
        return [msg, json_walkers]

    @staticmethod
    def getWalkerInfoOfTokenOwner(walker_id):
        walker = Walker.getFromWalkerIdWithinUser(walker_id, g.currentUser)
        if walker:
            [trails, json_trails] = Walker.getTrails(walker)
            msg = 'walker info'
        else:
            msg = 'wrong walker id'
        return [msg, walker.walker_name, json_trails]

    @staticmethod
    def run(shell_walker_executor):
        shell_walker_executor.run()
        thread.exit()


class ShellWalkerExecutor(object):
    def __init__(self, shell_mission, private_key_file='~/.ssh/id_rsa',
                 become_pass=None):
        self.shell_mission = shell_mission
        self.walker = shell_mission.getWalker()
        [trails, json_trails] = shell_mission.getTrails()
        self.trails = trails
        self.owner = self.walker.getOwner()
        self.hostnames = shell_mission.getIplist()
        self.remote_user = shell_mission.osuser
        run_data = {
            'walker_id': self.walker.walker_id,
            'user_id': self.owner.user_id
        }
        self.shell_exec_adpater = ShellExecAdapter(
            self.hostnames,
            self.remote_user,
            private_key_file,
            run_data,
            become_pass,
            shell_mission.shell)

    def run(self):
        [state, stats_sum, results] = self.shell_exec_adpater.run()
        self.walker.state = state
        self.walker.save()
        for trail in self.trails:
            host_result = results[trail.ip]
            host_stat_sum = stats_sum[trail.ip]
            trail.resultUpdate(host_stat_sum, host_result)
            trail.save()
        try:
            thread.exit()
            msg = 'walker<' + self.walker.walker_id + '> thread exit.'
        except:
            msg = 'walker<' + self.walker.walker_id + '> thread cannot exit.'
        app.logger.info(msg)
