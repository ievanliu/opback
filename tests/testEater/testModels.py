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
        # initialize os
        os1 = OperatingSystem('os-1', 'Linux', 'CentOS7.1')
        os2 = OperatingSystem('os-2', 'Windows', 'Win10')
        db.session.add_all([os1, os2])
        # initialize osuser
        user1 = OSUser('u-1', 'elk', '111111', '0')
        user2 = OSUser('u-2', 'zabbix', '111111', '0')
        user3 = OSUser('u-3', 'joch', '111111', '1')
        db.session.add_all([user1, user2, user3])
        # initialize user2os
        os1.user = [user1, user3]
        os2.user.append(user2)
        os2.user.append(user3)
        # initialize interface
        if1 = Interface('if-1', 'eth0')
        if2 = Interface('if-2', 'eth1')
        if3 = Interface('if-3', 'eth2')
        db.session.add_all([if1, if2, if3])
        # initialize computer specification
        cs1 = ComputerSpecification('cs-1', '1330Hz', 4, '32G', '200G')
        cs2 = ComputerSpecification('cs-2', '1670Hz', 8, '32G', '200G')
        cs3 = ComputerSpecification('cs-3', '3330Hz', 32, '256G', '600G')
        db.session.add_all([cs1, cs2,cs3])
        # initialize pm
        pm1 = PhysicalMachine('pm-1', 'iqn-1','gp-1', 'cs-2', 'NFJD-PM-1', 'host-pm-1', '20160701', 'os-1')
        pm2 = PhysicalMachine('pm-2', 'iqn-2','gp-2', 'cs-2', 'NFJD-PM-2', 'host-pm-2', '20160701', 'os-1')
        pm3 = PhysicalMachine('pm-3', 'iqn-3','gp-3', 'cs-3', 'NFJD-PM-3', 'host-pm-3', '20160701', 'os-2')
        db.session.add_all([pm1, pm2, pm3])
        # initialize vm
        vm1 = VirtualMachine('vm-1', 'pm-1', '6189', 'iqn-4', 'gp-1', 'cs-2', 'NFJD-VM-1', 'host-vm-1', '20160701', 'os-1')
        vm2 = VirtualMachine('vm-2', 'pm-2', '6007', 'iqn-5', 'gp-1', 'cs-2', 'NFJD-VM-2', 'host-vm-2', '20160701', 'os-2')
        vm3 = VirtualMachine('vm-3', 'pm-2', '6009', 'iqn-6', 'gp-3', 'cs-2', 'NFJD-VM-3', 'host-vm-3', '20160701', 'os-2')
        vm4 = VirtualMachine('vm-4', 'pm-3', '61899', 'iqn-7','gp-2', 'cs-1', 'NFJD-VM-4', 'host-vm-4', '20160701', 'os-1')
        db.session.add_all([vm1, vm2, vm3, vm4])
        # initialize osuser2it
        pm1.osuser = [user1, user3]
        pm2.osuser = [user2]
        vm1.osuser = [user1]
        vm3.osuser = [user1, user2]
        # initialize ip
        ip1 = IP('ip-1', '192.168.182.1', '255.255.255.0', 'if-1', 'pm-1', 'pm')
        ip2 = IP('ip-2', '192.168.182.2', '255.255.255.0', 'if-1', 'pm-2', 'pm')
        ip3 = IP('ip-3', '192.168.182.3', '255.255.255.0', 'if-1', 'pm-3', 'pm')
        ip4 = IP('ip-4', '10.0.100.3', '255.255.255.0', 'if-2', 'pm-3', 'pm')
        ip5 = IP('ip-5', '192.168.182.4', '255.255.255.0', 'if-1', 'vm-1', 'vm')
        ip6 = IP('ip-6', '192.168.182.5', '255.255.255.0', 'if-1', 'vm-2', 'vm')
        ip7 = IP('ip-7', '192.168.182.6', '255.255.255.0', 'if-1', 'vm-3', 'vm')
        ip8 = IP('ip-8', '192.168.182.7', '255.255.255.0', 'if-1', 'vm-4', 'vm')
        ip9 = IP('ip-9', '192.168.182.254', '255.255.255.0', 'if-1', 'vm-1', 'vip')
        ip10 = IP('ip-10', '192.168.182.253', '255.255.255.0', 'if-1', 'pm-2', 'vip')
        db.session.add_all([ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8, ip9, ip10])
        # initialize rack
        rack1 = Rack('rack-1', 'CMCC-RACK-1', 'pm-1')
        rack2 = Rack('rack-2', 'CMCC-RACK-2', 'pm-2')
        rack3 = Rack('rack-3', 'CMCC-RACK-3', 'pm-3')
        rack4 = Rack('rack-4', 'CMCC-RACK-4', 'pm-3')
        db.session.add_all([rack1, rack2, rack3, rack4])
        # do committing
        db.session.commit()

    # drop db
    def tearDown(self):
        db.session.close()
        db.drop_all(bind=self.default_bind_key)

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
        cs0 = ComputerSpecification('cs-cs', '1330Hz', 8, '64G', '1T')
        eq_(cs0.__repr__(), "<ComputerSpecification %r>" % cs0.id)
        db.session.add(cs0)
        db.session.commit()
        # 0.1 check cols test
        cols, relations, isColComplete, isRelComplete = \
            cs0.checkColumnsAndRelations(
                id='cs-p', cpu_num=8, __table__='lalal', computer=None)
        eq_(cols,  {'cpu_num': 8, 'id': 'cs-p'})
        eq_(relations, {'computer': None})
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
