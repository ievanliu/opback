
import sys
sys.path.append('.')

from nose.tools import *
import json
import os
from tecstack import app, db

# from tecstack.vminfo.services import VMINFOListAPI, VMINFOAPI
from utils import *
from tecstack.vminfo.models import VirtualMachine, PhysicalMachine, PublicIP

class TestVminfoModels():
    '''
        Unit test for VMINFOListAPI and VMINFOAPI.
    '''

    def setUp(self):
        app.testing = True
        app.config['DB_FILE'] = 'test.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                        os.path.join(app.config['DB_FOLDER'],
                        app.config['DB_FILE'])

#        if not os.path.exists(app.config['DB_FOLDER']):
#            os.mkdir(app.config['DB_FOLDER'])

        self.tester = app.test_client(self)
        db.create_all()


    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_virtualmachine_getinfo(self):
        # v1 = Vm_info_tab('CIDC-R-01-000-VM-00000622',
        #                  'CIDC-R-01-090-SRV-00002588', 'BCI000002d4',
        #                  '192.168.41.11', '20121018145925',
        #                  'CIDC-R-01-000-VN-00000790', 2)
        # v2 = Vm_info_tab('CIDC-R-01-000-VM-00000658',
        #                  'CIDC-R-01-013-SRV-00002068', 'BCI000002fb',
        #                  '192.168.62.14', '20121022162725',
        #                  'CIDC-R-01-000-VN-00000811', 2)
        # db.session.add(v1)
        # db.session.add(v2)
        # db.session.commit()
        # '''
        # Get VMINFO list.
        # '''
        # args = dict(page=1, pp=1)
        # response = self.tester.get(
        #     '/api/v0.0/vminfos',
        #     content_type="application/json",
        #     data=json.dumps(args))
        # eq_(response.status_code, 200)
        # check_content_type(response.headers)
        # v = json.loads(response.data)
        # vminfos = v['vm_infos']
        # eq_(1, len(vminfos))
        # eq_(2, v['total_page'])
        test_vm_id = "CIDC-R-01-000-VM-00000236"
        vm_info = VirtualMachine.query.filter_by(VM_ID=test_vm_id).first()
        eq_(vm_info.VM_Name, "BCI000001523")

    @with_setup(setUp, tearDown)
    def test_virtualmachine_addinfo(self):
        vm = VirtualMachine('CIDC-R-01-000-VM-00000622',
                         'CIDC-R-01-090-SRV-00002588', 'BCI000002d4',
                         '192.168.41.11', '20121018145925',
                         'CIDC-R-01-000-VN-00000790', 2) 
        db.session.add(vm)
        db.session.commit()
        test_vm_id = "CIDC-R-01-000-VM-00000622"
        vm_info = VirtualMachine.query.filter_by(VM_ID=test_vm_id).first()
        eq_(vm_info.VM_Name, "BCI000002d4")        

    @with_setup(setUp, tearDown)
    def test_virtualmachine_delete(self):
        test_vm_id = "CIDC-R-01-000-VM-00000236"
        db.session.delete(VirtualMachine.query.filter_by(VM_ID=vm_id).first())
        db.session.commit()



    # @with_setup(setUp, tearDown)
    # def test_vminfo_get(self):
    #     '''
    #     Get a VMINFO.
    #     '''
    #     response = self.tester.get(
    #         '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000658',
    #         content_type="application/json")
    #     eq_(response.status_code, 200)
    #     check_content_type(response.headers)
    #     v = json.loads(response.data)
    #     eq_(1, len(v))
    #     vminfo = v['vm_info']
    #     eq_(7, len(vminfo))
    #     eq_('CIDC-R-01-000-VM-00000658', vminfo['vm_id'])

    # @with_setup(setUp, tearDown)
    # def test_vminfo_post(self):
    #     '''
    #     Post new VMINFO.
    #     '''
    #     args = dict(vm_id='CIDC-R-01-000-VM-00000236',
    #         pm_id='CIDC-R-01-046-SRV-00002381',
    #         vm_name='BCI00000152', ip='192.168.62.10',
    #         creater_time='20121011112416',
    #         vn_id='CIDC-R-01-000-VN-00000811',
    #         vm_status=2)
    #     response = self.tester.post(
    #         '/api/v0.0/vminfos',
    #         content_type='application/json',
    #         data=json.dumps(args))
    #     check_content_type(response.headers)
    #     eq_(response.status_code, 201)
    #     v = json.loads(response.data)
    #     eq_(1, len(v))
    #     vminfo = v['vm_info']
    #     eq_(7, len(vminfo))
    #     eq_('CIDC-R-01-000-VM-00000236', vminfo['vm_id'])

    # @with_setup(setUp,tearDown)
    # def test_vminfo_put(self):
    #     '''
    #     Put/Update existing VMINFO.
    #     pay attension to the difference between dict and json string.
    #     {'test':'test'} vs. '{"test":"test"}'
    #     '''
    #     d = dict(vm_name='BCI000003e7', ip='192.168.53.26')
    #     response = self.tester.put(
    #         '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000622',
    #         content_type='application/json',
    #         data=json.dumps(d))
    #     check_content_type(response.headers)
    #     eq_(response.status_code, 201)
    #     v = json.loads(response.data)
    #     vminfo = v['vm_info']
    #     eq_('BCI000003e7', vminfo['vm_name'])
    #     eq_('192.168.53.26', vminfo['ip'])

    # @with_setup(setUp,tearDown)
    # def test_vminfo_delete(self):
    #     '''
    #     Delete existing VMINFO.
    #     '''
    #     response = self.tester.delete(
    #         '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000658')
    #     eq_(response.status_code, 204)
