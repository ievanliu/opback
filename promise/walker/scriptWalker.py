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
from .models import Walker, ScriptMission, Script
from . import utils as walkerUtils
from .. import app
from ..ansiAdapter.ansiAdapter import ScriptExecAdapter
from .. import utils
from ..user import auth
# import threading
# import thread
from .. import dont_cache

# threadLock = threading.Lock()


class ScriptWalkerAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ScriptWalkerAPI, self).__init__()

    """
    Establish a script mission walker, it will return the walker id.
    A walker may have several trails(target hosts).
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    def post(self):
        # check the arguments
        [iplist, script, os_user, params, walker_name] = self.argCheckForPost()
        # setup a walker
        walker = Walker(walker_name)

        [msg, trails] = walker.establish(iplist, g.current_user)
        # setup a scriptmission and link to the walker
        script_mission = ScriptMission(script, os_user, params, walker)
        script_mission.save()
        walker.state = -1
        walker.save()
#        # setup a shell mission walker executor thread#

#        try:
#            script_walker_executor = ScriptWalkerExecutor(script_mission)
#            # run the executor thread
#            script_walker_executor.start()#

#            msg = 'target script execution established!'
#            return {'message': msg, 'walker_id': walker.walker_id}, 200#

#        except:
#            msg = 'faild to establish mission.'
#            walker.state = -4
#            walker.save()
#            return {'message': msg, 'walker_id': walker.walker_id}, 200

        script_walker_executor = ScriptWalkerExecutor(script_mission)
        # run the executor thread
        # script_walker_executor.start()
        script_walker_executor.run()

        msg = 'target script execution established!'
        return {'message': msg, 'walker_id': walker.walker_id}, 200

    """
    find out all the script-mission walkers or one of them
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    @dont_cache()
    def get(self):
        walker_id = self.argCheckForGet()
        if not walker_id:
            [msg, json_walkers] = self.getWalkerListOfTokenOwner()
            return {'message': msg, 'walkers': json_walkers}, 200
        else:
            [msg, walker_name, state, json_trails] = \
                self.getWalkerInfoOfTokenOwner(walker_id)
            return {
                'message': msg,
                'walker_name': walker_name,
                'state': state,
                'trails': json_trails}, 200

    """
    arguments check methods
    """
    def argCheckForPost(self):
        self.reqparse.add_argument(
            'iplist', type=list, location='json',
            required=True, help='iplist ip must be a list')
        self.reqparse.add_argument(
            'scriptid', type=str, location='json',
            required=True, help='script_id must be a string')
        self.reqparse.add_argument(
            'params', type=list, location='json',
            help='params must be a string')
        self.reqparse.add_argument(
            'osuser', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'name', type=str, location='json',
            help='default walker-name: time-scriptname')

        args = self.reqparse.parse_args()
        iplist = args['iplist']
        # cheak all IPs of the iplist
        for ip in iplist:
            if not walkerUtils.ipFormatChk(ip):
                msg = 'wrong ip address'
                raise utils.InvalidAPIUsage(msg)
        script_id = args['scriptid']
        params = args['params']
        os_user = args['osuser']
        walker_name = args['name']

        # check if the script belongs to the current user
        script = Script.getFromIdWithinUserOrPublic(
            script_id, g.current_user)
        if script:
            if not walker_name:
                walker_name = str(walkerUtils.serialCurrentTime()) + \
                    '-' + str(script.script_name)
            if params:
                params = " ".join(params)
            else:
                params = None
            return [iplist, script, os_user, params, walker_name]
        else:
            msg = 'wrong script id.'
            raise utils.InvalidAPIUsage(msg)

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

        [walkers, json_walkers] = Walker.getScriptMissionWalker(g.current_user)
        msg = 'walker list of ' + g.current_user.username
        return [msg, json_walkers]

    @staticmethod
    def getWalkerInfoOfTokenOwner(walker_id):
        [walker, json_walker] = Walker.getFromWalkerIdWithinUser(
            walker_id, g.current_user)
        if walker:
            [trails, json_trails] = walker.getTrails()
            msg = 'walker info'
            return [msg, walker.walker_name, walker.state, json_trails]
        else:
            msg = 'wrong walker id'
            raise utils.InvalidAPIUsage(msg)

#    @staticmethod
#    def run(shell_walker_executor):
#        shell_walker_executor.run()
#        thread.exit()


class ScriptAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(ScriptAPI, self).__init__()

    """
    insert a new script.
    """
    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    def post(self):
        # check the arguments
        [script_name, script_text, script_lang, is_public] = \
            self.argCheckForPost()

        # create a script object
        script = Script(
            script_name, script_text, g.current_user, script_lang, is_public)
        script.save()
        msg = 'script created.'
        return {'message': msg, 'script_id': script.script_id}, 200

    @auth.PrivilegeAuth(privilegeRequired='scriptExec')
    def put(self):
        # check the arguments
        [script_id, script_name, script_text, script_lang, is_public] = \
            self.argCheckForPut()
        # modify target script object
        [script, jsonScript] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if script:
            script.update(
                script_name, script_text, script_lang, g.current_user,
                is_public)
            script.save()
            msg = 'script<id:' + script.script_id + '>uptaded'
            return {'message': msg}, 200
        else:
            msg = 'wrong script id or its not your script'
            raise utils.InvalidAPIUsage(msg)

    @auth.PrivilegeAuth(privilegeRequired="scriptExec")
    @dont_cache()
    def get(self):
        script_id = self.argCheckForGet()
        if not script_id:
            callableScripts = Script.getCallableScripts(g.current_user)
            json_callableScripts = list()
            for callableScript in callableScripts:
                result = dict()
                result['script_id'] = callableScript.Script.script_id
                result['script_name'] = callableScript.Script.script_name
                result['script_text'] = callableScript.Script.script_text
                result['owner_name'] = callableScript.User.username
                result['owner_id'] = callableScript.Script.owner_id
                result['time_create'] = callableScript.Script.time_create
                result['time_last_edit'] = callableScript.Script.time_last_edit
                result['is_public'] = callableScript.Script.is_public
                result['script_lang'] = callableScript.Script.script_lang
                json_callableScripts.append(result)
            msg = 'got script list.'
            return {'message': msg, 'scripts': json_callableScripts}, 200
        else:
            callableScript = Script.getCallableScripts(
                g.current_user, script_id)
            if callableScript:
                result = dict()
                result['script_id'] = callableScript.Script.script_id
                result['script_name'] = callableScript.Script.script_name
                result['script_text'] = callableScript.Script.script_text
                result['owner_name'] = callableScript.User.username
                result['owner_id'] = callableScript.Script.owner_id
                result['time_create'] = callableScript.Script.time_create
                result['time_last_edit'] = callableScript.Script.time_last_edit
                result['is_public'] = callableScript.Script.is_public
                result['script_lang'] = callableScript.Script.script_lang
                msg = 'got target script.'
                return {'message': msg, 'script': result}, 200
            else:
                raise utils.InvalidAPIUsage(msg)

    @auth.PrivilegeAuth(privilegeRequired='scriptExec')
    def delete(self):
        script_id = self.argCheckForDelete()
        [script, jsonScript] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if not script:
            msg = 'wrong script_id.'
            raise utils.InvalidAPIUsage(msg)
        [state, msg] = script.setInvalid()
        if state:
            return {'message': msg}, 200
        else:
            raise utils.InvalidAPIUsage(msg)

    """
    arguments check methods
    """
    def argCheckForGet(self):
        self.reqparse.add_argument(
            'script_id', type=str,
            location='args', help='script id must be a string')
        args = self.reqparse.parse_args()
        script_id = args['script_id']
        if not script_id:
            script_id = None
        return script_id

    def argCheckForPost(self):
        self.reqparse.add_argument(
            'script_name', type=str, location='json',
            required=True, help='iplist ip must be a list')
        self.reqparse.add_argument(
            'script_text', type=unicode, location='json',
            required=True, help='script_text must be a unicode text')
        self.reqparse.add_argument(
            'script_lang', type=str, location='json',
            required=True, help='osuser must be a string')
        self.reqparse.add_argument(
            'is_public', type=int, location='json',
            required=True, help='is_public must be 0 or 1')
        args = self.reqparse.parse_args()
        script_name = args['script_name']
        script_text = args['script_text']
        script_lang = args['script_lang']
        is_public = args['is_public']
        return [script_name, script_text, script_lang, is_public]

    def argCheckForPut(self):
        self.reqparse.add_argument(
            'script_id', type=str, location='args',
            required=True, help='script_id must be a string')
        self.reqparse.add_argument(
            'script_name', type=str, location='json',
            required=True, help='iplist_name must be a list')
        self.reqparse.add_argument(
            'script_text', type=unicode, location='json',
            required=True, help='script_text must be a unicode text')
        self.reqparse.add_argument(
            'script_lang', type=str, location='json',
            required=True, help='script_lang must be a string')
        self.reqparse.add_argument(
            'is_public', type=int, location='json',
            required=True, help='is_public must be 0 or 1')
        args = self.reqparse.parse_args()
        script_id = args['script_id']
        script_name = args['script_name']
        script_text = args['script_text']
        script_lang = args['script_lang']
        is_public = args['is_public']
        return [script_id, script_name, script_text, script_lang, is_public]

    def argCheckForDelete(self):
        self.reqparse.add_argument(
            'script_id', type=str, required=True,
            location='args', help='script id must be a string')
        args = self.reqparse.parse_args()
        script_id = args['script_id']
        return script_id

    @staticmethod
    def getScriptListOfTokenOwner():
        [scripts, json_scripts] = Script.getWithinUser(g.current_user)
        if json_scripts:
            msg = 'scripts info'
            return [msg, json_scripts]
        else:
            msg = 'no scripts exist.'
            return [msg, None]

    @staticmethod
    def getExcutableScriptsInfo():
        pass

    @staticmethod
    def getScriptInfo(script_id):
        [script, json_script] = Script.getFromIdWithinUser(
            script_id, g.current_user)
        if script:
            msg = 'walker info'
            return [msg, json_script]
        else:
            msg = 'wrong script id'
            return [msg, None]


# class ScriptWalkerExecutor(threading.Thread):
class ScriptWalkerExecutor(Resource):
    def __init__(self, script_mission, private_key_file='~/.ssh/id_rsa',
                 become_pass=None):
        # threading.Thread.__init__(self)
        self.script_mission = script_mission
        self.walker = script_mission.getWalker()
        self.script = script_mission.getScript()
        [trails, json_trails] = script_mission.getTrails()
        self.trails = trails
        self.owner = self.walker.getOwner()
        self.hostnames = script_mission.getIplist()
        self.remote_user = script_mission.osuser
        run_data = {
            'walker_id': self.walker.walker_id,
            'user_id': self.owner.user_id
        }
        self.script_exec_adpater = ScriptExecAdapter(
            self.hostnames,
            self.remote_user,
            private_key_file,
            run_data,
            become_pass,
            self.script.script_text,
            script_mission.params)

    def run(self):
        msg = 'walker<id:' + self.walker.walker_id + '> begin to run.'
        app.logger.info(utils.logmsg(msg))

        [state, stats_sum, results] = self.script_exec_adpater.run()
        # threadLock.acquire()
        for trail in self.trails:
            host_result = results[trail.ip]
            host_stat_sum = stats_sum[trail.ip]
            trail.resultUpdate(host_stat_sum, host_result)
            trail.save()
        self.walker.state = state
        self.walker.save()
        # threadLock.release()

        msg = 'walker<id:' + self.walker.walker_id + \
            '>scriptExecutor task finished.'
        app.logger.info(utils.logmsg(msg))
        # thread.exit()
