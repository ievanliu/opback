# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: Aug 6, 2016
#
# This is the task module of eater package.

from .. import app, utils
from .schedules import celery
from ..zabber.models import Host, HostGroup
from .models import ITEquipment, IP, Group
import random

__DoraemonUpdateNotify = 'Doraemon Update Notify: %s.'


@celery.task(bind=True, name='host_sync')
def host_sync(self):
    """
        Update host relative infos.
        From Zabber to Eater.
    """
    try:
        # mark the beginning
        msg = __DoraemonUpdateNotify % \
            'hey guys, it\'s time to update the hosts'
        app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(0, 20)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # 1. get hostgroup
        hostgroups = HostGroup().get()
        # Model Group synchronization for eater
        group = Group()
        for hg in hostgroups:
            g = group.update(id=hg['groupid'], name=hg['name'])
            if not g:
                g = group.insert(id=hg['groupid'], name=hg['name'])
            if g:
                msg = __DoraemonUpdateNotify % ('<Group %s>' % g['id'])
                app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 50)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

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
                msg = __DoraemonUpdateNotify % ('<ITEquipment %s>' % t['id'])
                app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 70)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

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
                    msg = __DoraemonUpdateNotify % ('<IP %s>' % p['id'])
                    app.logger.info(utils.logmsg(msg))
        # for progress bar
        prog = random.randint(prog, 100)
        self.update_state(
            state='PROGRESS',
            meta={'current': prog, 'total': 100, 'message': ''})

        # mark the end
        msg = __DoraemonUpdateNotify % 'Host Infos are Up-to-the-Minute'
        app.logger.info(utils.logmsg(msg))
        return {'current': 100, 'total': 100, 'message': msg}
    except Exception as e:
        # mark the errors
        app.logger.error(utils.logmsg(e))
        msg = __DoraemonUpdateNotify % \
            'Error occurs while updating Host Infos.'
        app.logger.error(utils.logmsg(msg))
        return {'current': 100, 'total': 100, 'message': msg}
