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

        app.config['DB_FILEPATH'] = os.path.join(app.config['DB_FOLDER'], app.config['DB_FILE'])
        rv = sqlite3.connect(app.config['DB_FILEPATH'])
        rv.row_factory = sqlite3.Row
        with app.open_resource(app.config['DB_SOURCEFILEPATH'], mode='r') as f:
            rv.cursor().executescript(f.read())
        rv.commit()
        rv.close()

    # drop db
    def tearDown(self):
        db.drop_all()

    # test to insertting data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_insertinfo(self):
        vm = VirtualMachine('TEST-R-01-000-VM-00000622',
                         'TEST-R-01-090-SRV-00002588', 'BCI000002d4',
                         '192.168.41.11', '20121018145925',
                         'TEST-R-01-000-VN-00000790', 2) 
        db.session.add(vm)
        db.session.commit()

        vm = VirtualMachine.query.filter_by(VM_ID="TEST-R-01-000-VM-00000622").first()
        eq_(vm.VM_Name, "BCI000002d4")
    
    # test to deleting data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_deleteinfo(self):
        db.session.delete(VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000597").first())
        db.session.commit()

        vm = VirtualMachine.query.filter_by(VM_ID="TEST-R-01-000-VM-00000597").first()
        eq_(vm, None)

    # test to updating data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_updateinfo(self):
        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000236").first()
        vm.VM_Name = "TEST00002d4"
        db.session.commit()

        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000236").first()
        eq_(vm.VM_Name, "TEST00002d4")

    # test to get data
    @with_setup(setUp, tearDown)
    def test_virtualmachine_getinfo(self):
        vm = VirtualMachine.query.filter_by(VM_ID="CIDC-R-01-000-VM-00000236").first()
        eq_(vm.VM_Name, "BCI00000152")



