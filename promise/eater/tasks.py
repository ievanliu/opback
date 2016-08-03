# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 27, 2016
#
# This is the task module of eater package.

from .. import app, utils
from .schedules import celery
from ..zabber.models import Host, HostGroup
from .models import ITEquipment, IP, Group

UpdateNotify = 'Update Notify: %s.'


@celery.task(name='host_sync')
def host_sync():
    """
        Update host relative infos.
        From Zabber to Eater.
    """
    # mark the beginning
    msg = UpdateNotify % 'hey guys, it\'s time to update the hosts'
    app.logger.info(utils.logmsg(msg))
    # 1. get hostgroup
    hostgroups = HostGroup().get()
    # Model Group synchronization for eater
    group = Group()
    for hg in hostgroups:
        g = group.update(id=hg['groupid'], name=hg['name'])
        if not g:
            g = group.insert(id=hg['groupid'], name=hg['name'])
        if g:
            msg = UpdateNotify % ('<Group %s>' % g['id'])
            app.logger.info(utils.logmsg(msg))
    # 2. get host
    hosts = Host().get()
    # Model ITEquipment synchronization for eater
    it = ITEquipment()
    for h in hosts:
        g = [group.getObject(i) for i in [y['groupid']
             for y in [x for x in h['groups']]]]
        t = it.update(id=h['hostid'], label=h['host'],
                      name=h['name'], group=g)
        if not t:
            t = it.insert(id=h['hostid'], label=h['host'],
                          name=h['name'], group=g)
        if t:
            msg = UpdateNotify % ('<ITEquipment %s>' % t['id'])
            app.logger.info(utils.logmsg(msg))
    # Model IP synchronization for eater
    ip = IP()
    for h in hosts:
        inf = h['interfaces']
        if inf:
            # use first ip as default
            p = ip.update(id=inf[0]['interfaceid'],
                          ip_addr=inf[0]['ip'], it_id=h['hostid'])
            if not p:
                p = ip.insert(id=inf[0]['interfaceid'],
                              ip_addr=inf[0]['ip'], it_id=h['hostid'])
            if p:
                msg = UpdateNotify % ('<IP %s>' % p['id'])
                app.logger.info(utils.logmsg(msg))
    # mark the end
    msg = UpdateNotify % 'Host Infos are Up-to-the-Minute'
    app.logger.info(utils.logmsg(msg))
