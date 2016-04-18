# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Apr 15, 2016
#
# This is the hostgroup api module of cmdb package,
# with method GET, POST, PUT, DELETE.
#
from flask.ext.restful import reqparse, Resource
from .models import HostGroup, Host, HostInterface
from ..user import auth
from .. import app, utils


class HostGroupListAPI(Resource):
    """
        HostGroupList Restful API.
        for GET (Readonly)
    """
    def __init__(self):
        super(HostGroupListAPI, self).__init__()
        self.parser = reqparse.RequestParser()

    # get host group list
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        data = HostGroup().get()
        return {'data': data}, 200


class HostGroupAPI(Resource):
    """
        HostGroup Restful API.
        for GET, POST, PUT, DELETE
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
        self.parser.add_argument(
            'name', type=str, help='group name must be str')

    # get info of a hostgroup by groupid
    def get(self, groupid):
        # 1. constraint check
        hg = HostGroup()
        if not hg.exists(groupid=groupid):
            msg = self.__GroupNotFound % {'groupid': groupid}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404
        # 2. get execution
        # 2.1 get hostgroup basic info
        data = hg.get(groupid=groupid)[0]
        # 2.2 get host(s) of the hostgroup
        h = Host()
        hs = h.get(groupid=groupid)
        hosts = []
        if hs:           
            hif = HostInterface()
            for host in hs:
                host['interfaces'] = hif.get(hostid=host['hostid'])
                host['interfacecount'] = hif.getCount(hostid=host['hostid'])
                hosts.append(host)
        data['hosts'] = hosts
        # 2.3 get count of hosts in the hostgroup
        data['hostcount'] = h.getCount(groupid)
        return {'data': data}, 200

    # create a new hostgroup
    def post(self):
        # 1. parameter availability check
        args = self.parser.parse_args()
        name = args['name']
        if not name:
            msg = self.__ParamsIllegal % {'name': name}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404
        # 2. constraint check
        hg = HostGroup()
        if hg.exists(name=name):
            msg = self.__GroupExisting % {'name': name}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 403
        # 3. create execution
        data = {'groupid': hg.create(name)['groupids'][0]}
        return {'data': data}, 201

    # update an existing hostgroup
    def put(self, groupid):
        # 1. parameter availability check
        args = self.parser.parse_args()
        name = args['name']
        if not name:
            msg = self.__ParamsIllegal % 'all null'
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404
        # 2. constraint check
        hg = HostGroup()
        if not hg.exists(groupid=groupid):
            msg = self.__GroupNotFound % {'groupid': groupid}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404
        if hg.exists(name=name):
            msg = self.__GroupExisting % {'name': name}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 403
        # 3. update execution
        data = {'groupid': hg.update(groupid, name)['groupids'][0]}
        return {'data': data}, 201

    # delete an existing hostgroup
    def delete(self, groupid):
        # 1. constraint check
        hg = HostGroup()
        if not hg.exists(groupid=groupid):
            msg = self.__GroupNotFound % {'groupid': groupid}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404
        # 2. delete execution
        data = {'groupid': hg.delete(groupid)['groupids'][0]}
        return {'data': data}, 204
