# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 25, 2016
#
# This is the api module of eater package.


from flask.ext.restful import reqparse, Resource, inputs
from .models import ITEquipment, Group
from ..user import auth
from .. import app, utils


"""
    Data Services
"""


class HostListAPI(Resource):
    """
        HostList Restful API.
        Supported By Eater.
        Methods: GET (Readonly)
    """
    params = ['category', 'label', 'name', 'os_id', 'setup_time']

    def __init__(self):
        super(HostListAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        # page
        self.parser.add_argument(
            'page', type=inputs.positive,
            help='Page must be a positive integer')
        # pp: number of items per page
        self.parser.add_argument(
            'pp', type=inputs.positive,
            help='PerPage must be a positive integer', dest='per_page')
        # search parameters
        for x in self.params:
            self.parser.add_argument(x, type=str)

    # get whole list of hosts existing
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        pages, data, kw = False, [], {}
        args = self.parser.parse_args()
        for x in self.params:
            if args[x]:
                kw[x] = args[x]
        page = args['page']
        if kw or not page:
            data = ITEquipment().get(**kw)
        else:
            query = []
            per_page = args['per_page']
            if per_page:
                query = ITEquipment().get(page, per_page, **kw)
            else:
                query = ITEquipment().get(page, **kw)
            if query:
                data, pages = query[0], query[1]
        return {'totalpage': pages, 'data': data}, 200


class HostAPI(Resource):
    """
        Host Restful API.
        Supported By Eater.
        for GET (Readonly)
    """
    # define custom error msg
    __ParamsIllegal = 'Parameter Illegal: %s.'
    __HostNotFound = 'Host Not Found: %s.'
    __HostExisting = 'Host Already Existing: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    def __init__(self):
        super(HostAPI, self).__init__()
        self.parser = reqparse.RequestParser()

    # get info of a host by hostid
    def get(self, hostid):
        it = ITEquipment().get(id=hostid, depth=2)
        if it:
            data = it[0]
            return {'data': data}, 200
        else:
            msg = self.__HostNotFound % {'id': hostid}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404


class HostGroupListAPI(Resource):
    """
        HostGroupList Restful API.
        Supported By Eater.
        for GET (Readonly)
    """
    params = ['name']

    def __init__(self):
        super(HostGroupListAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        # page
        self.parser.add_argument(
            'page', type=inputs.positive,
            help='page must be a positive integer')
        # pp: number of items per page
        self.parser.add_argument(
            'pp', type=inputs.positive,
            help='perpage must be a positive integer', dest='perpage')
        # search parameters
        for x in self.params:
            self.parser.add_argument(x, type=str)

    # get host group list
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        pages, data, kw = False, [], {}
        args = self.parser.parse_args()
        for x in self.params:
            if args[x]:
                kw[x] = args[x]
        page = args['page']
        if kw or not page:
            data = Group().get(**kw)
        else:
            query = []
            per_page = args['per_page']
            if per_page:
                query = Group().get(page, per_page, **kw)
            else:
                query = Group().get(page, **kw)
            if query:
                data, pages = query[0], query[1]
        return {'totalpage': pages, 'data': data}, 200


class HostGroupAPI(Resource):
    """
        HostGroup Restful API.
        Supported By Eater.
        for GET (Readonly)
    """
    # define custom error msg
    __ParamsIllegal = 'Parameter Illegal: %s.'
    __GroupNotFound = 'Group Not Found: %s.'
    __GroupExisting = 'Group Already Existing: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    def __init__(self):
        super(HostGroupAPI, self).__init__()
        self.parser = reqparse.RequestParser()

    # get info of a hostgroup by groupid
    def get(self, groupid):
        group = Group().get(id=groupid, depth=2)
        if group:
            data = group[0]
            return {'data': data}, 200
        else:
            msg = self.__GroupNotFound % {'id': groupid}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404


"""
    Task Services
"""
from .tasks import host_sync


class HostSyncAPI(Resource):
    """
        Host Synchronization Restful API.
        Supported By Eater.
        for GET (Readonly)
    """
    # define custom error msg
    __ExeFailed = 'Execute Failed: %s.'
    __CheckFailed = 'Check Failed: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    def __init__(self):
        super(HostSyncAPI, self).__init__()
        self.parser = reqparse.RequestParser()

    # execute a host synchronization task
    def post(self):
        try:
            t = host_sync.apply_async()
            return {'id': t.task_id}, 201
        except Exception as e:
            msg = self.__ExeFailed % e
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 500

    # get a host synchronization task status
    def get(self, taskid):
        try:
            task = host_sync.AsyncResult(taskid)
            result = {
                'id': task.id,
                'state': task.state,
                'info': task.info
            }
            return {'result': result}, 200
        except Exception as e:
            msg = self.__CheckFailed % e
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 500
