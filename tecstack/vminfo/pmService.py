# @author: leannmak
# @last revised: 24/7/2015 16:25
# @version 0.0
# Service Description:
# GET	get all PMs			http://host:port/api/v0.0/pminfos
# GET	get PMs by page		http://host:port/api/v0.0/pminfos?page=2&pp=20
# 							page:current page / pp:number of items per page
# GET		get a PM 		http://host:port/api/v0.0/pminfos/<string:PM_id>
# POST		add a PM		http://host:port/api/v0.0/pminfos
# PUT		update a PM		http://host:port/api/v0.0/pminfos/<string:PM_id>
# DELETE	delete a PM		http://host:port/api/v0.0/pminfos/<string:PM_id>
# GET	get VMs via a PM	http://host:port/api/v0.0/pminfos/help/<string:PM_id>

# all the imports
from flask_restful import reqparse, Resource, inputs
from tecstack import db
from models import PhysicalMachine


'''
    PMINFOList API
'''


class PMINFOListAPI(Resource):

    # request parsing:
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # page
        self.reqparse.add_argument(
            'page', type=inputs.positive,
            help='Page must be a positive integer')
        # pp: number of items per page
        self.reqparse.add_argument(
            'pp', type=inputs.positive,
            help='PerPage must be a positive integer', dest='per_page')
        super(PMINFOListAPI, self).__init__()

    # get the PM list (paging done)
    def get(self):
        args = self.reqparse.parse_args()
        page = args['page']
        if not page:
            query = PhysicalMachine.query.order_by(PhysicalMachine.PM_ID).all()
            pms = [row.to_json() for row in query]
            return {'pm_infos': pms}, 200
        else:
            per_page = args['per_page']
            if not per_page:
                # set default
                per_page = 20
            query = PhysicalMachine.query.paginate(page, per_page, False)
            pms = [row.to_json() for row in query.items]
            return {'total_page': query.pages, 'pm_infos': pms}, 200


'''
    PMINFO API : visit by unique PM_id
'''


class PMINFOAPI(Resource):

    # request parsing
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'pm_id', type=str, help='PM_ID must be a string')
        self.reqparse.add_argument(
            'pm_name', type=str, help='PM_Name must be a string')
        self.reqparse.add_argument(
            'ip', type=inputs.regex(r'^(\d{1,3}\.){3}\d{1,3}$'),
            help='IP must be a string like XXX.XXX.XXX.XXX')
        self.reqparse.add_argument(
            'creat_time', type=str, help='Creat_Time must be a string')
        self.reqparse.add_argument(
            'iscsi_name', type=str, help='iscsiName must be a string')
        super(PMINFOAPI, self).__init__()

    # get a single PM
    def get(self, pm_id):
        pm_info = PhysicalMachine.query.filter_by(PM_ID=pm_id).first()
        if not pm_info:
            return {'error': 'PM %s Not Found' % pm_id}, 404
        return {'pm_info': pm_info.to_json()}, 200

    # add a new PM
    def post(self):
        try:
            args = self.reqparse.parse_args()
            pm_id = args['pm_id']
            if pm_id:
                old_pm = PhysicalMachine.query.filter_by(PM_ID=pm_id).first()
                if not old_pm:
                    new_pm = PhysicalMachine(
                        pm_id=pm_id, pm_name=args['pm_name'], ip=args['ip'],
                        creat_time=args['creat_time'],
                        iscsi_name=args['iscsi_name'])
                    db.session.add(new_pm)
                    db.session.commit()
                    return {'pm_info': new_pm.to_json()}, 201
                else:
                    return {'error': 'PM %s Already Existed' % pm_id}, 403
            else:
                return {'error': 'PM_ID must not be NULL'}, 400
        except Exception as e:
            return {'error': e}, 500

    # delete a PM
    def delete(self, pm_id):
        try:
            old_pm = PhysicalMachine.query.filter_by(PM_ID=pm_id).first()
            if old_pm:
                db.session.delete(old_pm)
                db.session.commit()
                return {}, 204
            else:
                return {'error': 'PM %s Not Found' % pm_id}, 404
        except Exception as e:
            return {'error': e}, 500

    # update a PM
    def put(self, pm_id):
        try:
            pm = PhysicalMachine.query.filter_by(PM_ID=pm_id).first()
            if pm:
                args = self.reqparse.parse_args()
                pm_name = args['pm_name']
                if pm_name:
                    pm.PM_Name = pm_name
                ip = args['ip']
                if ip:
                    pm.IP = ip
                creat_time = args['creat_time']
                if creat_time:
                    pm.Creat_Time = creat_time
                iscsi_name = args['iscsi_name']
                if iscsi_name:
                    pm.iscsiName = iscsi_name
                db.session.commit()
                return {'pm_info': pm.to_json()}, 201
            else:
                return {'error': 'PM %s Not Found' % pm_id}, 404
        except Exception as e:
            return {'error': e}, 500


'''
    PMHELP API : view more by PM_id
'''


class PMHELPAPI(Resource):

    # get additional infos to current PM
    def get(self, pm_id):
        pm_info = PhysicalMachine.query.filter_by(PM_ID=pm_id).first()
        if not pm_info:
            return {'error': 'PM %s Not Found' % pm_id}, 404
        vm_info = pm_info.vm_info
        vms = [row.to_json() for row in vm_info if vm_info]
        help_list = [{'vm_id': vm['vm_id'], 'vm_name': vm['vm_name'],
                     'ip': vm['ip']} for vm in vms]
        return {'help_info': help_list}, 200
