# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 12, 2016
#
# This is autotest for cmdb models of eater package.

import sys
sys.path.append('.')

from nose.tools import *
import json
import os

from sqlite3 import dbapi2 as sqlite3

from promise import app, db
from promise.eater.models import *

class TestModels():
    '''
        Unit test for models in Eater
    '''
    default_bind_key = None

    # establish db
    def setUp(self):
        app.testing = True

        # database for test
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])

        self.tester = app.test_client(self)

        # database initialization
        # db.drop_all(bind=self.default_bind_key)
        db.create_all(bind=self.default_bind_key)

        # table initialization
        # initialize osuser
        user1 = OSUser(id='u-1', name='elk', password='111111', privilege='0')
        user2 = OSUser(id='u-2', name='zabbix', password='111111', privilege='0')
        user3 = OSUser(id='u-3', name='joch', password='111111', privilege='1')
        db.session.add_all([user1, user2, user3])
        # initialize os
        os1 = OperatingSystem(user = [user1, user3], id='os-1', name='Linux', version='CentOS7.1')
        os2 = OperatingSystem(user=[user2, user3], id='os-2', name='Windows', version='Win10')
        db.session.add_all([os1, os2])
        # # initialize user2os
        # os1.user = [user1, user3]
        # os2.user.append(user2)
        # os2.user.append(user3)
        # initialize interface
        if1 = Interface(id='if-1', name='eth0')
        if2 = Interface(id='if-2', name='eth1')
        if3 = Interface(id='if-3', name='eth2')
        db.session.add_all([if1, if2, if3])
        # initialize computer specification
        cs1 = ComputerSpecification(id='cs-1', cpu_fre='1330Hz', cpu_num=4, memory='32G', disk='200G')
        cs2 = ComputerSpecification(id='cs-2', cpu_fre='1670Hz', cpu_num=8, memory='32G', disk='200G')
        cs3 = ComputerSpecification(id='cs-3', cpu_fre='3330Hz', cpu_num=32, memory='256G', disk='600G')
        db.session.add_all([cs1, cs2,cs3])
        # initialize pm
        pm1 = PhysicalMachine(osuser = [user1, user3], id='pm-1', iqn_id='iqn-1', group_id='gp-1', spec_id='cs-2', label='NFJD-PM-1', name='host-pm-1', setup_time='20160701', os_id='os-1')
        pm2 = PhysicalMachine(osuser = [user2], id='pm-2', iqn_id='iqn-2', group_id='gp-2', spec_id='cs-2', label='NFJD-PM-2', name='host-pm-2', setup_time='20160701', os_id='os-1')
        pm3 = PhysicalMachine(id='pm-3', iqn_id='iqn-3', group_id='gp-3', spec_id='cs-3', label='NFJD-PM-3', name='host-pm-3', setup_time='20160701', os_id='os-2')
        db.session.add_all([pm1, pm2, pm3])
        # initialize vm
        vm1 = VirtualMachine(osuser = [user1], id='vm-1', pm_id='pm-1', vm_pid='6189', iqn_id='iqn-4', group_id='gp-1', spec_id='cs-2', label='NFJD-VM-1', name='host-vm-1', setup_time='20160701', os_id='os-1')
        vm2 = VirtualMachine(id='vm-2', pm_id='pm-2', vm_pid='6007', iqn_id='iqn-5', group_id='gp-1', spec_id='cs-2', label='NFJD-VM-2', name='host-vm-2', setup_time='20160701', os_id='os-2')
        vm3 = VirtualMachine(osuser = [user1, user2], id='vm-3', pm_id='pm-2', vm_pid='6009', iqn_id='iqn-6', group_id='gp-3', spec_id='cs-2', label='NFJD-VM-3', name='host-vm-3', setup_time='20160701', os_id='os-2')
        vm4 = VirtualMachine(id='vm-4', pm_id='pm-3', vm_pid='61899', iqn_id='iqn-7', group_id='gp-2', spec_id='cs-1', label='NFJD-VM-4', name='host-vm-4', setup_time='20160701', os_id='os-1')
        db.session.add_all([vm1, vm2, vm3, vm4])
        # # initialize osuser2it
        # pm1.osuser = [user1, user3]
        # pm2.osuser = [user2]
        # vm1.osuser = [user1]
        # vm3.osuser = [user1, user2]
        # initialize ip
        ip1 = IP(id='ip-1', ip_addr='192.168.182.1', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-1', ip_category='pm')
        ip2 = IP(id='ip-2', ip_addr='192.168.182.2', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-2', ip_category='pm')
        ip3 = IP(id='ip-3', ip_addr='192.168.182.3', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-3', ip_category='pm')
        ip4 = IP(id='ip-4', ip_addr='10.0.100.3', ip_mask='255.255.255.0', if_id='if-2', it_id='pm-3', ip_category='pm')
        ip5 = IP(id='ip-5', ip_addr='192.168.182.4', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-1', ip_category='vm')
        ip6 = IP(id='ip-6', ip_addr='192.168.182.5', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-2', ip_category='vm')
        ip7 = IP(id='ip-7', ip_addr='192.168.182.6', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-3', ip_category='vm')
        ip8 = IP(id='ip-8', ip_addr='192.168.182.7', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-4', ip_category='vm')
        ip9 = IP(id='ip-9', ip_addr='192.168.182.254', ip_mask='255.255.255.0', if_id='if-1', it_id='vm-1', ip_category='vip')
        ip10 = IP(id='ip-10', ip_addr='192.168.182.253', ip_mask='255.255.255.0', if_id='if-1', it_id='pm-2', ip_category='vip')
        db.session.add_all([ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9, ip10])
        # initialize rack
        rack1 = Rack(id='rack-1', label='CMCC-RACK-1', it_id='pm-1')
        rack2 = Rack(id='rack-2', label='CMCC-RACK-2', it_id='pm-2')
        rack3 = Rack(id='rack-3', label='CMCC-RACK-3', it_id='pm-3')
        rack4 = Rack(id='rack-4', label='CMCC-RACK-4', it_id='pm-3')
        db.session.add_all([rack1, rack2, rack3, rack4])
        # do committing
        db.session.commit()

    # drop db
    def tearDown(self):
        db.session.close()
        db.drop_all(bind=self.default_bind_key)

    # model relationships test
    @with_setup(setUp, tearDown)
    def test_model_init(self):
        '''
        test model initialization
        '''
        vm = VirtualMachine.query.filter_by(id='vm-1').first()
        it1 = ITEquipment.query.filter_by(id=vm.id).first()
        eq_(vm.label, it1.label)
        # eq_(vm.columns()['id'].nullable, it1.columns()['label'].nullable)
        # eq_(vm.relationships(), None)
        # eq_(vm.relationships()['osuser'].secondary, None)
        eq_(vm.relationships()['ip'].secondary, None)
        eq_(VirtualMachine.__mapper__.columns.__dict__['_data']['id'].nullable, False)


    # model relationships test
    @with_setup(setUp, tearDown)
    def test_model_relationships(self):
        '''
        test relationships in eater
        '''
        # 1. os and osuser
        os = OperatingSystem.query.filter_by(id='os-1').first()
        user = OSUser.query.filter_by(id='u-1').first()
        assert user in os.user
        assert os in user.os
        # 2. osuser and it_equipment
        # 2.1 osuser and vm
        vm = VirtualMachine.query.filter_by(id='vm-1').first()
        it1 = ITEquipment.query.filter_by(id=vm.id).first()
        assert user in vm.osuser
        assert it1 in user.it
        # 2.2 osuser and pm
        pm = PhysicalMachine.query.filter_by(id='pm-1').first()
        it2 = ITEquipment.query.filter_by(id=pm.id).first()
        assert user in pm.osuser
        assert it2 in user.it
        # 3. pm and vm
        assert vm in pm.vm
        eq_(vm.pm_id, pm.id)
        eq_(vm.pm, pm)
        # 4. ip and it_equipment
        # 4.1 ip and pm
        ip1 = IP.query.filter_by(id='ip-9').first()
        assert ip1 in vm.ip
        eq_(ip1.it_id, vm.id)
        eq_(it1, ip1.it)
        # 4.2 ip and vm
        ip2 = IP.query.filter_by(id='ip-1').first()
        assert ip2 in pm.ip
        eq_(ip2.it_id, pm.id)
        eq_(it2, ip2.it)
        # 5. ip and interface
        inf = Interface.query.filter_by(id='if-1').first()
        assert ip1 in inf.ip
        eq_(ip1.inf, inf)
        assert ip2 in inf.ip
        eq_(ip2.inf, inf)
        # 6. computer_specification and computer
        # 6.1 computer_specification and vm
        cs = ComputerSpecification.query.filter_by(id='cs-2').first()
        eq_(vm.spec, cs)
        pc1 = Computer.query.filter_by(id=vm.id).first()
        assert pc1 in cs.computer
        # 6.2 computer_specification and pm
        pc2 = Computer.query.filter_by(id=pm.id).first()
        eq_(pm.spec, cs)
        assert pc2 in cs.computer
        # 7. it_equipment and rack
        # 7.1 pm and rack
        rack = Rack.query.filter_by(id='rack-1').first()
        assert rack in pm.rack
        eq_(it2, rack.it)

    # IP model test
    @with_setup(setUp, tearDown)
    def test_ip_insert(self):
        '''
        maintain an IP
        '''
        pass
        # 1. insert an IP
        # 2. query an IP
        # 3. update an IP
        # 4. delete an IP

        # computer specification model test

    # computer specification model test
    @with_setup(setUp, tearDown)
    def test_computer_specification(self):
        '''
        maintain a computer specification
        '''
        # 0. common test
        # 0.0 print test
        cs0 = ComputerSpecification(id='cs-cs', cpu_fre='1330Hz', cpu_num=8, memory='64G', disk='1T')
        eq_(cs0.__repr__(), "<ComputerSpecification %r>" % cs0.id)
        db.session.add(cs0)
        db.session.commit()
        # 0.1 check cols test
        cols, relations, isColComplete, isRelComplete = \
            cs0.checkColumnsAndRelations(
                id='cs-p', cpu_num=8, __table__='lalal', computer=None)
        eq_(cols,  {'cpu_num': 8, 'id': 'cs-p'})
        eq_(relations, {})
        # 1. insert a ComputerSpecification
        # 1.1 totally new specification
        cs1 = ComputerSpecification().insert(
            cpu_fre='1330Hz', cpu_num=4, memory='64G', disk='300G')
        eq_(cs1['cpu_num'], 4)
        eq_(cs1['computer'], [])
        # 1.2 existing specification
        cs2 = ComputerSpecification().insert(
            cpu_fre='1330Hz', cpu_num=4, memory='32G', disk='200G')
        eq_(cs2, None)
        # 2. query a ComputerSpecification
        # 2.1 by id or other factor
        cs3 = ComputerSpecification().get(id=cs1['id'])
        eq_(cs3[0]['disk'], '300G')
        # 2.2 all
        cs_list = ComputerSpecification().get()
        eq_(len(cs_list), 5)
        assert cs0,cs1 in cs_list
        # 3. update a ComputerSpecification
        # 3.1 non duplicative: update successfully
        cs4 = ComputerSpecification().update(id=cs1['id'], cpu_num=8)
        eq_(cs4['cpu_num'], 8)
        cs5 = ComputerSpecification().get(id=cs1['id'])
        eq_(cs5[0]['cpu_num'], 8)
        # 3.2 duplicative: update failed
        cs6 = ComputerSpecification().update(id=cs0.id, disk='300G')
        eq_(cs6, None)
        # 4. delete a ComputerSpecification
        # 4.1 specification exists
        flag = ComputerSpecification().delete(cs1['id'])
        eq_(flag, True)
        flag = ComputerSpecification().delete(cs0.id)
        eq_(flag, True)
        # 4.2 no such specification
        flag = ComputerSpecification().delete('boomshakalaka')
        eq_(flag, False)
        cs_list = ComputerSpecification().get()
        eq_(len(cs_list), 3)
        eq_(cs_list[0]['id'], 'cs-1')
        eq_(cs_list[1]['id'], 'cs-2')
        eq_(cs_list[2]['id'], 'cs-3')

    # computer specification model test
    @with_setup(setUp, tearDown)
    def test_virtual_machine(self):
        '''
        maintain a virtual machine
        '''
        # 1. query a virtual machine
        # 1.1 has conditions
        vm0 = VirtualMachine.query.filter_by(iqn_id='iqn-4').first()
        vm = VirtualMachine().get(iqn_id='iqn-4')
        eq_(hasattr(VirtualMachine, '__table__'), True)
        eq_(hasattr(Doraemon, '__table__'), False)
        # eq_(MyModel.__bases__, True)
        eq_(VirtualMachine.__bases__[0].__name__, 'Computer')
        # eq_(VirtualMachine.__mapper__.relationships.__dict__['_data'], None)
        # eq_(VirtualMachine.__mapper__.columns.__dict__['_data'], None)
        # eq_((super(VirtualMachine, vm0)).__dict__, object)
        # eq_(vm[0], None)
        eq_(vm[0]['id'], 'vm-1')
        eq_(vm[0]['pm'][0]['id'], 'pm-1')
        # 1.2 all
        vm_list = VirtualMachine().get()
        eq_(len(vm_list), 4)
        assert vm[0] in vm_list
