
from nose.tools import *
import json
import os
from tecstack import app, db
from tecstack.vminfo.pmService import PMINFOListAPI, PMINFOAPI, PMHELPAPI
from utils import *
from tecstack.vminfo.models import VirtualMachine, PhysicalMachine

class TestPminfoApi():
    '''
        Unit test for PMINFOListAPI and PMINFOAPI.
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
            'iqn.1994-05.com.redhat:665a944a8')
        p2 = PhysicalMachine('CIDC-R-01-004-SRV-00002010',
            'NFJD-PSC-IBMH-SV128', '172.16.1.133',
            '20120615180101',
            'iqn.1994-05.com.redhat:665a933a8')
        db.session.add(v1)
        db.session.add(v2)
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()

    def tearDown(self):
        db.drop_all()

    @with_setup(setUp, tearDown)
    def test_pminfo_list_get_all(self):
        '''
        Get PMINFO list.
        '''
        response = self.tester.get(
            '/api/v0.0/pminfos',
            content_type="application/json",
            data=json.dumps({}))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        p = json.loads(response.data)
        eq_(2, len(p['pm_infos']))

    @with_setup(setUp, tearDown)
    def test_pminfo_list_get_by_page(self):
        '''
        Get PMINFO list by page.
        '''
        args = dict(page=2, pp=1)
        response = self.tester.get(
            '/api/v0.0/pminfos',
            content_type="application/json",
            data=json.dumps(args))
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        p = json.loads(response.data)
        pminfos = p['pm_infos']
        eq_(1, len(pminfos))
        eq_(2, p['total_page'])

    @with_setup(setUp, tearDown)
    def test_pminfo_get(self):
        '''
        Get a PMINFO.
        '''
        # 1. PM existing
        response = self.tester.get(
            '/api/v0.0/pminfos/CIDC-R-01-004-SRV-00002009',
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        v = json.loads(response.data)
        eq_(1, len(v))
        pminfo = v['pm_info']
        eq_(5, len(pminfo))
        eq_('CIDC-R-01-004-SRV-00002009', pminfo['pm_id'])
        # 2. PM not existing
        response = self.tester.get(
            '/api/v0.0/pminfos/CIDC-R-01-004-SRV-00002011',
            content_type="application/json")
        eq_(response.status_code, 404)
        v = json.loads(response.data)
        eq_('PM CIDC-R-01-004-SRV-00002011 Not Found', v['error'])

    @with_setup(setUp, tearDown)
    def test_pminfo_post(self):
        '''
        Post new PMINFO.
        '''
        # 1. PM not existing
        args = dict(
            pm_id='CIDC-R-01-046-SRV-00002381',
            pm_name='NFJD-PSC-IBMH-SV129',
            ip='172.16.1.132',
            creat_time='20121011112416',
            iscsi_name='iqn.1994-05.com.redhat:665a922a8')
        response = self.tester.post(
            '/api/v0.0/pminfos',
            content_type='application/json',
            data=json.dumps(args))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        p = json.loads(response.data)
        eq_(1, len(p))
        pminfo = p['pm_info']
        eq_(5, len(pminfo))
        eq_('CIDC-R-01-046-SRV-00002381', pminfo['pm_id'])
        # 2. PM existing
        args = dict(
            pm_id='CIDC-R-01-004-SRV-00002009',
            pm_name='NFJD-PSC-IBMH-SV129',
            ip='172.16.1.132',
            creat_time='20120615180101',
            iscsi_name='iqn.1994-05.com.redhat:665a944a8')
        response = self.tester.post(
            '/api/v0.0/pminfos',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 403)
        # 3. PM_ID is NULL
        args = dict(
            pm_name='NFJD-PSC-IBMH-SV132',
            ip='172.16.1.135',
            creat_time='20120615180503',
            iscsi_name='iqn.1994-05.com.redhat:665a966a8')
        response = self.tester.post(
            '/api/v0.0/pminfos',
            content_type='application/json',
            data=json.dumps(args))
        eq_(response.status_code, 400)

    @with_setup(setUp,tearDown)
    def test_pminfo_put(self):
        '''
        Put/Update existing PMINFO.
        pay attension to the difference between dict and json string.
        {'test':'test'} vs. '{"test":"test"}'
        '''
        d = dict(pm_name='NFJD-PSC-IBMH-SV156', ip='192.168.53.76')
        # 1. PM existing
        response = self.tester.put(
            '/api/v0.0/pminfos/CIDC-R-01-004-SRV-00002009',
            content_type='application/json',
            data=json.dumps(d))
        check_content_type(response.headers)
        eq_(response.status_code, 201)
        p = json.loads(response.data)
        pminfo = p['pm_info']
        eq_('NFJD-PSC-IBMH-SV156', pminfo['pm_name'])
        eq_('192.168.53.76', pminfo['ip'])
        # 2. PM not existing
        response = self.tester.put(
            '/api/v0.0/pminfos/CIDC-R-01-004-SRV-00002133',
            content_type='application/json',
            data=json.dumps(d))
        eq_(response.status_code, 404)

    @with_setup(setUp,tearDown)
    def test_pminfo_delete(self):
        '''
        Delete existing PMINFO.
        '''
        # 1. PM existing
        response = self.tester.delete(
            '/api/v0.0/pminfos/CIDC-R-01-004-SRV-00002010')
        eq_(response.status_code, 204)
        # 2. PM not existing
        response = self.tester.delete(
            '/api/v0.0/pminfos/CIDC-R-01-004-SRV-00002011')
        eq_(response.status_code, 404)

    @with_setup(setUp, tearDown)
    def test_pmhelp_get(self):
        '''
        Get HELPINFO for a PM.
        '''
        # 1. PM existing
        response = self.tester.get(
            '/api/v0.0/pminfos/help/CIDC-R-01-004-SRV-00002009',
            content_type="application/json")
        eq_(response.status_code, 200)
        check_content_type(response.headers)
        v = json.loads(response.data)
        eq_(1, len(v))
        help_info = v['help_info']
        eq_(2, len(help_info))
        eq_('CIDC-R-01-000-VM-00000622', help_info[0]['vm_id'])
        # 2. PM not existing
        response = self.tester.get(
            '/api/v0.0/pminfos/help/CIDC-R-01-004-SRV-00002011')
        eq_(response.status_code, 404)
