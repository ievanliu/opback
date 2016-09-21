# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 10, 2016
#
# This is the interface module of eater package.

from .models import Network, IP


def toForward(ip_list):
    """ Inventory Args Interface for Forward """
    if ip_list and (isinstance(ip_list, list) or isinstance(ip_list, tuple)):
        option = (
            'enable_pass', 'model', 'name', 'vender', 'osuser', 'con_pass',
            'connect', 'method', 'port', 'ip', 'id')
        inventory = []
        network = Network()
        for x in ip_list:
            ip = IP.query.filter_by(ip_addr=x).first()
            id = ip.it_id if ip else None
            if id:
                y = network.get(id=id, depth=3, option=option)
                if y:
                    y = y[0]
                    d = dict(ip=x, actpass=y['enable_pass'])
                    d['model'] = y['model'][0]['name'] if y['model'] else ''
                    d['vender'] = y['model'][0]['vender'] if y['model'] else ''
                    d['connection'] = []
                    connect = None
                    for k in y['ip']:
                        if k['id'] == ip.id:
                            connect = k['connect']
                            break
                    if connect:
                        if y['osuser']:
                            for m in y['osuser']:
                                for k in m['connect']:
                                    if k in connect:
                                        d['connection'].append(dict(
                                            connect=k['method'],
                                            remote_port=k['port'],
                                            remote_user=m['name'],
                                            conpass=m['con_pass'],
                                            user_id=m['id']))
                    inventory.append(d)
            else:
                pass
        return inventory
