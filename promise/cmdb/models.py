# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Apr 15, 2016
#
# This is the model module based on zabbix for the cmdb package.
#
from .zapi import ZabbixAPI


class HostGroup(object):
    """
        HostGroup Model based on Zabbix.
    """
    # define a standard zabbix api object name
    default_object_name = "Hostgroup"

    def __init__(self):
        # call for standard zabbix api
        self.__zapi = ZabbixAPI()
        # login to zabbix server
        self.__zapi.login()
        # create a standard zabbix api object 'Hostgroup'
        self.__zapiobj = self.__zapi.__getattr__(self.default_object_name)

    # create a new hostgroup
    # 'name' is the only property to be defined
    def create(self, name):
        params = {'name': name}
        result = self.__zapiobj.proxy_method(
            '%s.create' % self.default_object_name, params)
        return result

    # delete a hostgroup by groupid (only parameter to be used)
    def delete(self, groupid):
        params = [groupid]
        result = self.__zapiobj.proxy_method(
            '%s.delete' % self.default_object_name, params)
        return result

    # check hostgroup existence by grouid or name
    # 'groupid' and 'name' are strictly unique for a hostgroup
    # pls check it before create, get, update, delete
    def exists(self, groupid='', name=''):
        params = {}
        if groupid:
            params['groupid'] = groupid
        if name:
            params['name'] = name
        result = self.__zapiobj.proxy_method(
            '%s.exists' % self.default_object_name, params)
        return result

    # get hostgroup(s) by groupid or related hostid
    # such as 'templateids', 'triggerids', ... are supported
    # here using 'groupids' and 'hostids' only
    def get(self, groupid='', hostid=''):
        params = {}
        if hostid:
            params['hostids'] = hostid
        if groupid:
            params['groupids'] = groupid
        params['output'] = 'extend'
        result = self.__zapiobj.proxy_method(
            '%s.get' % self.default_object_name, params)
        return result

    # get a hostgroup object by groupid
    # only 'groupid' and 'name' are supported as search params
    # here using 'groupid' only
    def getObjects(self, groupid=''):
        params = {'groupid': groupid}
        result = self.__zapiobj.proxy_method(
            '%s.getobjects' % self.default_object_name,
            {'output': 'extend', 'filter': params})
        return result

    def isReachable(self, params):
        pass

    def isWritable(self, params):
        pass

    def massAdd(self, params):
        pass

    def massRemove(self, params):
        pass

    def massUpdate(self, params):
        pass

    # update a hostgroup by groupid
    # only 'groupid' are supported as search params
    # 'name' is the only property to be modified
    def update(self, groupid, name=''):
        params = {'groupid': groupid}
        if name:
            params['name'] = name
        result = self.__zapiobj.proxy_method(
            '%s.update' % self.default_object_name, params)
        return result

    # get count of hostgroups with given host
    def getCount(self, hostid=''):
        params = {'hostids': hostid}
        params['countOutput'] = 'true'
        result = self.__zapiobj.proxy_method(
            '%s.get' % self.default_object_name, params)
        return result


class Host(object):
    """
        Host Model based on Zabbix.
    """
    # define a standard zabbix api object name
    default_object_name = "Host"

    def __init__(self):
        self.__zapi = ZabbixAPI()
        self.__zapi.login()
        # create a standard zabbix api object 'Host'
        self.__zapiobj = self.__zapi.__getattr__(self.default_object_name)

    def create(self, params):
        pass

    def delete(self, hostid):
        pass

    # check host existence by hostid
    # 'hostid', 'host' and 'name' are strictly unique for a host
    # pls check it before create, get, update, delete
    def exists(self, hostid=''):
        params = {'hostid': hostid}
        result = self.__zapiobj.proxy_method(
            '%s.exists' % self.default_object_name, params)
        return result

    # get host(s) with given hostid or groupid(hostgroup)
    # such as 'itemids', 'applicationids', ... are supported
    # here using 'hostids' and 'groupids' only
    def get(self, hostid='', groupid=''):
        params = {}
        if hostid:
            params['hostids'] = hostid
        if groupid:
            params['groupids'] = groupid
        output = ["hostid", "host", "name", "status", "available"]
        params['output'] = output
        result = self.__zapiobj.proxy_method(
            '%s.get' % self.default_object_name, params)
        return result

    # get a host object by hostid
    def getObjects(self, hostid=''):
        params = {'hostid': hostid}
        result = self.__zapiobj.proxy_method(
            '%s.getobjects' % self.default_object_name, params)
        return result

    def isReachable(self, params):
        pass

    def isWritable(self, params):
        pass

    def massAdd(self, params):
        pass

    def massRemove(self, params):
        pass

    def massUpdate(self, params):
        pass

    def update(self, params):
        pass

    # get count of hosts in given hostgroup
    def getCount(self, groupid=''):
        params = {'groupids': groupid}
        params['countOutput'] = 'true'
        result = self.__zapiobj.proxy_method(
            '%s.get' % self.default_object_name, params)
        return result


class HostInterface(object):
    """
        HostInterface Model based on Zabbix.
    """
    # define a standard zabbix api object name
    default_object_name = "Hostinterface"

    def __init__(self):
        self.__zapi = ZabbixAPI()
        self.__zapi.login()
        # create a standard zabbix api object 'Hostinterface'
        self.__zapiobj = self.__zapi.__getattr__(self.default_object_name)

    def create(self, params):
        pass

    def delete(self, hostid):
        pass

    # check hostinterface existence by hostid, interfaceid, ip
    # 'dns' is also supported
    # here using 'hostid', 'interfaceid', 'ip' only
    def exists(self, hostid='', interfaceid='', ip=''):
        params = {}
        if hostid:
            params['hostid'] = hostid
        if interfaceid:
            params['interfaceid'] = interfaceid
        if ip:
            params['ip'] = ip
        result = self.__zapiobj.proxy_method(
            '%s.exists' % self.default_object_name, params)
        return result

    # get hostinterface(s) with given interfaceid or hostid
    # such as 'itemids', 'triggerids' are also supported
    # here using 'hostid' and 'interfaceid' only
    def get(self, hostid='', interfaceid=''):
        params = {}
        if hostid:
            params['hostids'] = hostid
        if interfaceid:
            params['interfaceids'] = interfaceid
        output = ["interfaceid", "hostid", "ip", "dns", "port"]
        params['output'] = output
        result = self.__zapiobj.proxy_method(
            '%s.get' % self.default_object_name, params)
        return result

    def massAdd(self, params):
        pass

    def massRemove(self, params):
        pass

    def replaceHostInterfaces(self, params):
        pass

    def update(self, params):
        pass

    # get count of hostinterfces in given host
    def getCount(self, hostid=''):
        params = {'hostids': hostid}
        params['countOutput'] = 'true'
        result = self.__zapiobj.proxy_method(
            '%s.get' % self.default_object_name, params)
        return result
