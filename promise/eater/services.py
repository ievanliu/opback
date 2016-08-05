# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 25, 2016
#
# This is the api module of eater package.


from flask.ext.restful import reqparse, Resource, inputs
from .models import ITEquipment
from ..user import auth
from .. import app, utils


class HostListAPI(Resource):
    """
        HostList Restful API.
        Supported By Eater.
        Methods: GET (Readonly)
    """
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

    # get whole list of hosts existing
    @auth.PrivilegeAuth(privilegeRequired="inventoryAdmin")
    def get(self):
        pages, data = False, []
        args = self.parser.parse_args()
        page = args['page']
        if not page:
            data = ITEquipment().get()
        else:
            query = []
            per_page = args['per_page']
            if per_page:
                query = ITEquipment().get(page, per_page)
            else:
                query = ITEquipment().get(page)
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
