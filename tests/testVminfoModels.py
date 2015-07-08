# coding:utf-8
# By Shawn Tai
# Jul,8,2015
# autotest for the vminfo models

import sys
sys.path.append('.')

from nose.tools import *
import json
import os
from tecstack import app, db
from sqlite3 import dbapi2 as sqlite3

# from tecstack.vminfo.services import VMINFOListAPI, VMINFOAPI
from utils import *
from tecstack.vminfo.models import VirtualMachine, PhysicalMachine, PublicIP


class TestModelsVirtualMachine():
    '''
        Unit test for model: VirtualMachine
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])

        if not os.path.exists(app.config['DB_FOLDER']):
            os.mkdir(app.config['DB_FOLDER'])

        self.tester = app.test_client(self)
        db.create_all()

        v1 = VirtualMachine('CIDC-R-01-000-VM-00000622',
            'CIDC-R-01-004-SRV-00002009', 'BCI000002d4',
            '192.168.41.11', '20121018145925',
            'CIDC-R-01-000-VN-00000790', 2)
        v2 = VirtualMachine('CIDC-R-01-000-VM-00000658',
            'CIDC-R-01-004-SRV-00002009', 'BCI000002fb',
            '192.168.62.14', '20121022162725',
            'CIDC-R-01-000-VN-00000811', 2)
        p1 = PhysicalMachine('CIDC-R-01-004-SRV-00002009', 
            'NFJD-PSC-IBMH-SV129', '172.16.1.132', 
            '20120615180101', 
            'iqn.1994-05.com.redhat:665a922a8')
        p2 = PhysicalMachine('CIDC-R-01-004-SRV-00002010',
            'NFJD-PSC-IBMH-SV130', '172.16.1.133',
            '20120615180101',
            'iqn.1994-05.com.redhat:d137da297aeb')
        db.session.add(v1)
        db.session.add(v2)
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_insertinfo(self):
        '''
        insert virtualmachine
        '''
        vm_insert = VirtualMachine('TEST-R-01-000-VM-00000623',
                         'TEST-R-01-090-SRV-00002588', 'BCI000002d4',
                         '192.168.41.11', '20121018145925',
                         'TEST-R-01-000-VN-00000790', 2) 
        db.session.add(vm_insert)
        db.session.commit()

        vm = VirtualMachine.query.filter_by(VM_ID="TEST-R-01-000-VM-00000623").first()
        eq_(vm.VM_Name, "BCI000002d4")
    
    # test to deleting data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_deleteinfo(self):
        '''
        delete virtualmachine
        '''
        db.session.delete(VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000622").first())
        db.session.commit()

        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000622").first()
        eq_(vm, None)

    # test to updating data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_updateinfo(self):
        '''
        updata virtualmachine
        '''
        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000622").first()
        vm.VM_Name = "TEST00002d4"
        db.session.commit()

        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000622").first()
        eq_(vm.VM_Name, "TEST00002d4")

    # test to get data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_getinfo(self):
        '''
        get virtualmachine&get Relate pm&to json
        '''
        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000622").first()
        vmDic = vm.to_json()
        pm = vm.pm
        eq_(vmDic['vm_name'], "BCI000002d4")
        eq_(pm.PM_Name, "NFJD-PSC-IBMH-SV129")



class TestModelsPhysicalMachine():
    '''
        Unit test for model: PhysicalMachine
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])

        if not os.path.exists(app.config['DB_FOLDER']):
            os.mkdir(app.config['DB_FOLDER'])

        self.tester = app.test_client(self)
        db.create_all()

        v1 = VirtualMachine('CIDC-R-01-000-VM-00000622',
            'CIDC-R-01-004-SRV-00002009', 'BCI000002d4',
            '192.168.41.11', '20121018145925',
            'CIDC-R-01-000-VN-00000790', 2)
        v2 = VirtualMachine('CIDC-R-01-000-VM-00000658',
            'CIDC-R-01-004-SRV-00002009', 'BCI000002fb',
            '192.168.62.14', '20121022162725',
            'CIDC-R-01-000-VN-00000811', 2)
        p1 = PhysicalMachine('CIDC-R-01-004-SRV-00002009', 
            'NFJD-PSC-IBMH-SV129', '172.16.1.132', 
            '20120615180101', 
            'iqn.1994-05.com.redhat:665a922a8')
        p2 = PhysicalMachine('CIDC-R-01-004-SRV-00002010',
            'NFJD-PSC-IBMH-SV130', '172.16.1.133',
            '20120615180101',
            'iqn.1994-05.com.redhat:d137da297aeb')
        db.session.add(v1)
        db.session.add(v2)
        db.session.add(p1)
        db.session.add(p2)

        db.session.commit()

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_physicalmachine_insertinfo(self):
        '''
        insert physicalmachine
        '''
        pm_insert = PhysicalMachine('TEST-R-01-004-SRV-00002009', 
            'NFJD-PSC-IBMH-SV129', '172.16.1.132', 
            '20120615180101', 
            'iqn.1994-05.com.redhat:665a922a8')
        db.session.add(pm_insert)
        db.session.commit()

        pm = PhysicalMachine.query.filter_by(PM_ID="TEST-R-01-004-SRV-00002009").first()
        eq_(pm.PM_Name, "NFJD-PSC-IBMH-SV129")
    
    # test to deleting data
    @with_setup(setUp, tearDown)
    def test_physicalmachine_deleteinfo(self):
        '''
        delete physicalmachine
        '''
        db.session.delete(PhysicalMachine.query.filter_by(PM_ID="CIDC-R-01-004-SRV-00002009").first())
        db.session.commit()

        pm = PhysicalMachine.query.filter_by(PM_ID="CIDC-R-01-004-SRV-00002009").first()
        eq_(pm, None)

    # test to updating data
    @with_setup(setUp, tearDown)
    def test_physicalmachine_updateinfo(self):
        '''
        pudate physicalmachine
        '''
        pm = PhysicalMachine.query.filter_by(PM_ID="CIDC-R-01-004-SRV-00002009").first()
        pm.PM_Name = "TEST-PSC-IBMH-SV129"
        db.session.commit()

        pm = PhysicalMachine.query.filter_by(PM_ID="CIDC-R-01-004-SRV-00002009").first()
        eq_(pm.PM_Name, "TEST-PSC-IBMH-SV129")

    # test to get data
    @with_setup(setUp, tearDown)
    def test_physicalmachine_getinfo(self):
        '''
        get physicalmachine&to json
        '''
        pm = PhysicalMachine.query.filter_by(PM_ID="CIDC-R-01-004-SRV-00002009").first()
        pmDic = pm.to_json()
        eq_(pmDic['pm_name'], "NFJD-PSC-IBMH-SV129")


class TestModelsPublicIP():
    '''
        Unit test for model: PublicIP
    '''
    # establish db
    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])

        if not os.path.exists(app.config['DB_FOLDER']):
            os.mkdir(app.config['DB_FOLDER'])

        self.tester = app.test_client(self)
        db.create_all()

        v1 = VirtualMachine('CIDC-R-01-000-VM-00000622',
            'CIDC-R-01-004-SRV-00002009', 'BCI000002d4',
            '192.168.41.11', '20121018145925',
            'CIDC-R-01-000-VN-00000790', 2)
        v2 = VirtualMachine('CIDC-R-01-000-VM-00000658',
            'CIDC-R-01-004-SRV-00002009', 'BCI000002fb',
            '192.168.62.14', '20121022162725',
            'CIDC-R-01-000-VN-00000811', 2)
        p1 = PhysicalMachine('CIDC-R-01-004-SRV-00002009', 
            'NFJD-PSC-IBMH-SV129', '172.16.1.132', 
            '20120615180101', 
            'iqn.1994-05.com.redhat:665a922a8')
        p2 = PhysicalMachine('CIDC-R-01-004-SRV-00002010',
            'NFJD-PSC-IBMH-SV130', '172.16.1.133',
            '20120615180101',
            'iqn.1994-05.com.redhat:d137da297aeb')
        ip1 = PublicIP('CIDC-R-01-002-IP-00037433',
            '1.2.14.93', '1', '10.102.240.18', 
            '20150521163200', '20150521163541')
        ip2 = PublicIP('CIDC-R-01-002-IP-00037434', 
            '1.2.14.94', '1', '10.102.240.19', 
            '20150522103129', '20150522103341')
        db.session.add(v1)
        db.session.add(v2)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(ip1)
        db.session.add(ip2)
        db.session.commit()

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_publicip_insertinfo(self):
        '''
        insert PublicIP
        '''
        ip_insert = PublicIP('TEST-R-01-002-IP-00037433',
            '1.2.14.99', '1', '10.102.240.18', 
            '20150521163200', '20150521163541')
        db.session.add(ip_insert)
        db.session.commit()

        ip = PublicIP.query.filter_by(Local_ID="TEST-R-01-002-IP-00037433").first()
        eq_(ip.IP, "1.2.14.99")
    
    # test to deleting data
    @with_setup(setUp, tearDown)
    def test_publicip_deleteinfo(self):
        '''
        delete PublicIP
        '''
        db.session.delete(PublicIP.query.filter_by(Local_ID="CIDC-R-01-002-IP-00037433").first())
        db.session.commit()

        ip = PublicIP.query.filter_by(Local_ID="CIDC-R-01-002-IP-00037433").first()
        eq_(ip, None)

    # test to updating data
    @with_setup(setUp, tearDown)
    def test_publicip_updateinfo(self):
        '''
        updata PublicIP
        '''
        ip = PublicIP.query.filter_by(Local_ID="CIDC-R-01-002-IP-00037433").first()
        ip.IP = "1.2.14.88"
        db.session.commit()

        ip = PublicIP.query.filter_by(Local_ID="CIDC-R-01-002-IP-00037433").first()
        eq_(ip.IP, "1.2.14.88")

    # test to get data
    @with_setup(setUp, tearDown)
    def test_publicip_getinfo(self):
        '''
        get PublicIP&to json
        '''
        ip = PublicIP.query.filter_by(Local_ID="CIDC-R-01-002-IP-00037433").first()
        ipDic = ip.to_json()
        eq_(ipDic['ip'], "1.2.14.93")





