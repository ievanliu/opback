
from nose.tools import *
import json
import os
from tecstack import app, db
from tecstack.vminfo.services import VMINFOListAPI, VMINFOAPI, VMHELPAPI
from utils import *
from tecstack.vminfo.models import VirtualMachine, PhysicalMachine, PublicIP

class TestVminfoApi():
    '''
        Unit test for VMINFOListAPI and VMINFOAPI.
    '''

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
        i1 = PublicIP('CIDC-R-01-002-IP-00037227', '1.2.13.148',
            '1', '192.168.41.11', '20150331093132', '20150331093541')
        i2 = PublicIP('CIDC-R-01-002-IP-00037224', '1.2.13.145',
            '1', '172.16.1.132', '20150611111055', '20150611111137')
        i3 = PublicIP('CIDC-R-01-002-IP-00037244', '1.2.13.165',
            '1', '192.168.62.14', '20150331150024', '20150401143030')
        db.session.add(v1)
        db.session.add(v2)
        db.session.add(p1)
        db.session.add(i1)
        db.session.add(i2)
        db.session.add(i3)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_vminfo_list_get_all(self):
        '''
        Get VMINFO list.
        '''
        response = self.tester.get(
            '/api/v0.0/vminfos',
            content_type="application/json",
            data=json.dumps({}))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        v = json.loads(response.data)
        eq_(2, len(v['vm_infos']))

    @with_setup(setUp, tearDown)
    def test_vminfo_list_get_by_page(self):
        '''
        Get VMINFO list by page.
        '''
        args = dict(page=2, pp=1)
        response = self.tester.get(
            '/api/v0.0/vminfos',
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        v = json.loads(response.data)
        vminfos = v['vm_infos']
        eq_(1, len(vminfos))
        eq_(2, v['total_page'])

    @with_setup(setUp, tearDown)
    def test_vminfo_get(self):
        '''
        Get a VMINFO.
        '''
        # 1. VM existing
        response = self.tester.get(
            '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000658',
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        v = json.loads(response.data)
        eq_(1, len(v))
        vminfo = v['vm_info']
        eq_(7, len(vminfo))
        eq_('CIDC-R-01-000-VM-00000658', vminfo['vm_id'])
        # 2. VM not existing
        response = self.tester.get(
            '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000657',
            content_type="application/json")
        eq_(response.status_code, 404)
        v = json.loads(response.data)
        eq_('VM CIDC-R-01-000-VM-00000657 Not Found', v['error'])

    @with_setup(setUp, tearDown)
    def test_vminfo_post(self):
        '''
        Post new VMINFO.
        '''
        # 1. VM not existing
        args = dict(vm_id='CIDC-R-01-000-VM-00000236',
            pm_id='CIDC-R-01-046-SRV-00002381',
            vm_name='BCI00000152', ip='192.168.62.10',
            creater_time='20121011112416',
            vn_id='CIDC-R-01-000-VN-00000811',
            vm_status=2)
        response = self.tester.post(
            '/api/v0.0/vminfos',
            content_type='application/json',
            data=json.dumps(args))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        v = json.loads(response.data)
        eq_(1, len(v))
        vminfo = v['vm_info']
        eq_(7, len(vminfo))
        eq_('CIDC-R-01-000-VM-00000236', vminfo['vm_id'])
        # 2. VM existing
        args = dict(vm_id='CIDC-R-01-000-VM-00000236',
            pm_id='CIDC-R-01-046-SRV-00002381',
            vm_name='BCI00000152', ip='192.168.62.10',
            creater_time='20121011112416',
            vn_id='CIDC-R-01-000-VN-00000811',
            vm_status=2)
        response = self.tester.post(
            '/api/v0.0/vminfos',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 403)
        # 3. VM_ID is NULL
        args = dict(
            pm_id='CIDC-R-01-046-SRV-00002381',
            vm_name='BCI00000152', ip='192.168.62.10',
            creater_time='20121011112416',
            vn_id='CIDC-R-01-000-VN-00000811',
            vm_status=2)
        response = self.tester.post(
            '/api/v0.0/vminfos',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 400)

    @with_setup(setUp,tearDown)
    def test_vminfo_put(self):
        '''
        Put/Update existing VMINFO.
        pay attension to the difference between dict and json string.
        {'test':'test'} vs. '{"test":"test"}'
        '''
        d = dict(vm_name='BCI000003e7', ip='192.168.53.26')
        # 1. VM existing
        response = self.tester.put(
            '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000622',
            content_type='application/json',
            data=json.dumps(d))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        v = json.loads(response.data)
        vminfo = v['vm_info']
        eq_('BCI000003e7', vminfo['vm_name'])
        eq_('192.168.53.26', vminfo['ip'])
        # 2. VM not existing
        response = self.tester.put(
            '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000657',
            content_type='application/json',
            data=json.dumps(d))
        eq_(response.status_code, 404)

    @with_setup(setUp,tearDown)
    def test_vminfo_delete(self):
        '''
        Delete existing VMINFO.
        '''
        # 1. VM existing
        response = self.tester.delete(
            '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000658')
        eq_(response.status_code, 204)
        # 2. VM not existing
        response = self.tester.delete(
            '/api/v0.0/vminfos/CIDC-R-01-000-VM-00000657')
        eq_(response.status_code, 404)

    @with_setup(setUp, tearDown)
    def test_vmhelp_get(self):
        '''
        Get HELPINFO for a VM.
        '''
        # 1. VM existing
        response = self.tester.get(
            '/api/v0.0/vminfos/help/CIDC-R-01-000-VM-00000622',
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        v = json.loads(response.data)
        eq_(1, len(v))
        help_info = v['help_info']
        eq_(4, len(help_info))
        eq_('1.2.13.148', help_info['vm_public_ip'])
        eq_('NFJD-PSC-IBMH-SV129', help_info['pm_name'])
        # 2. VM not existing
        response = self.tester.get(
            '/api/v0.0/vminfos/help/CIDC-R-01-000-VM-00000657')
        eq_(response.status_code, 404)
