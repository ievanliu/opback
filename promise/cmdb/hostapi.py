# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Apr 16, 2016
#
# This is the Host api module of cmdb package,
# with method GET（POST, PUT, DELETE unavailable now）.
#
from flask.ext.restful import reqparse, Resource
from .models import Host, HostGroup, HostInterface
from ..user import auth
from .. import app, utils


class HostListAPI(Resource):
    """
        HostList Restful API.
        for GET (Readonly)
    """
    def __init__(self):
        super(HostListAPI, self).__init__()
        self.parser = reqparse.RequestParser()

    # get whole list of hosts existing
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        data = Host().get()
        return {'data': data}, 200


class HostAPI(Resource):
    """
        Host Restful API.
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
        # 1. constraint check
        h = Host()
        if not h.exists(hostid=hostid):
            msg = self.__HostNotFound % {'hostid': hostid}
            app.logger.info(utils.logmsg(msg))
            return {'error': msg}, 404
        # 2. get execution
        # 2.1 get host basic info
        data = h.get(hostid=hostid)[0]
        # 2.2 get hostgroup(s) of the host
        hg = HostGroup()
        data['groups'] = hg.get(hostid=hostid)
        # 2.3 get count of the hostgroup
        data['groupcount'] = hg.getCount(hostid=hostid)
        # 2.3 get interface(s) of the host
        hif = HostInterface()
        data['interfaces'] = hif.get(hostid=hostid)
        # 2.4 get count of interfaces in the host
        data['interfacecount'] = hif.getCount(hostid=hostid)
        return {'data': data}, 200
