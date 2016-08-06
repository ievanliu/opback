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


class DoraemonListAPI(Resource):
    """
        Super DataList Restful API.
        Supported By Eater.
        Methods: GET (Readonly)

        Pay attention pls:
        Attributes 'parms' and 'obj' are asked during implementation.
        'params': a list of retrievable arguments of 'obj', can be [] or ().
        'obj': an instance of one of the models belonging to Eater.
    """
    __abstract__ = True

    # constructor
    def __init__(self, params, obj):
        super(DoraemonListAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        # page
        self.parser.add_argument(
            'page', type=inputs.positive,
            help='Page must be a positive integer')
        # pp: number of items per page
        self.parser.add_argument(
            'pp', type=inputs.positive,
            help='PerPage must be a positive integer', dest='per_page')
        setattr(self, 'params', params)
        for x in self.params:
            self.parser.add_argument(x, type=str)
        setattr(self, 'obj', obj)

    # get whole list of the object
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        pages, data, kw = False, [], {}
        args = self.parser.parse_args()
        for x in self.params:
            if args[x]:
                kw[x] = args[x]
        page = args['page']
        if kw or not page:
            data = self.obj.get(**kw)
        else:
            query = []
            per_page = args['per_page']
            if per_page:
                query = self.obj.get(page, per_page, **kw)
            else:
                query = self.obj.get(page, **kw)
            if query:
                data, pages = query[0], query[1]
        return {'totalpage': pages, 'data': data}, 200


class DoraemonAPI(Resource):
    """
        Super Data Restful API.
        Supported By Eater.
        for GET (Readonly)

        Pay attention pls:
        Attributes 'parms' and 'obj' are asked during implementation.
        'params': a list of attributes of 'obj', can be [] or ().
        'obj': an instance of one of the models belonging to Eater.
    """
    __abstract__ = True

    # define custom error msg
    __ParamsIllegal = 'Parameter Illegal: %s.'
    __ObjNotFound = 'Object Not Found: %s.'
    __ObjExisting = 'Object Already Existing: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    # constructor
    def __init__(self, params, obj):
        super(DoraemonAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        setattr(self, 'params', params)
        for x in self.params:
            self.parser.add_argument(x, type=str)
        setattr(self, 'obj', obj)

    # get a specific object
    def get(self, id):
        query = self.obj.get(id=id, depth=2)
        if query:
            data = query[0]
            return {'data': data}, 200
        else:
            msg = self.__ObjNotFound % {'id': id}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404


class HostListAPI(DoraemonListAPI):
    """
        HostList Restful API.
        Inherits from Super DataList API.
    """
    def __init__(self):
        params = ('category', 'label', 'name', 'os_id', 'setup_time')
        obj = ITEquipment()
        super(HostListAPI, self).__init__(params=params, obj=obj)


class HostAPI(DoraemonAPI):
    """
        Host Restful API.
        Inherits from Super Data API.
    """
    def __init__(self):
        params = []
        obj = ITEquipment()
        super(HostAPI, self).__init__(params=params, obj=obj)


class HostGroupListAPI(DoraemonListAPI):
    """
        HostGroupList Restful API.
        Inherits from Super DataList API.
    """
    def __init__(self):
        params = ['name']
        obj = Group()
        super(HostGroupListAPI, self).__init__(
            params=params, obj=obj)


class HostGroupAPI(DoraemonAPI):
    """
        HostGroup Restful API.
        Inherits from Super Data API.
    """
    def __init__(self):
        params = []
        obj = Group()
        super(HostGroupAPI, self).__init__(
            params=params, obj=obj)


"""
    Task Services
"""
from .tasks import host_sync


class DoraemonTaskAPI(Resource):
    """
        Super Task Restful API.
        Supported By Eater.
        for POST(Execute) / GET(Check).

        Pay attention pls:
        'task_name' is asked during implementation.
        'task_name': name of the task to be executed,
                     should be a string.
    """
    # define custom error msg
    __ExeFailed = 'Execute Failed: %s.'
    __CheckFailed = 'Check Failed: %s.'

    # add decorators for all
    decorators = [auth.PrivilegeAuth(
        privilegeRequired="inventoryAdmin")]

    # constructor
    def __init__(self, task_name):
        super(DoraemonTaskAPI, self).__init__()
        self.parser = reqparse.RequestParser()
        setattr(self, 'task_name', task_name)

    # execute a task
    def post(self):
        try:
            t = eval(self.task_name).apply_async()
            return {'id': t.task_id}, 201
        except Exception as e:
            msg = self.__ExeFailed % e
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 500

    # check a specific task status
    def get(self, id):
        try:
            task = eval(self.task_name).AsyncResult(id)
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


class HostSyncAPI(DoraemonTaskAPI):
    """
        Host Synchronization Restful API.
        Inherits from Super Task API.
    """
    def __init__(self):
        super(HostSyncAPI, self).__init__(
            task_name='host_sync')
