# @author: leannmak
# @last revision: 29/6/2015 22:04
# @version 0.0
# Service Description:
# GET get all VMs	http://host:port/api/v0.0/vminfos
# GET get VMs separated by page http://host:port/api/v0.0/vminfos?page=2&pp=20
#           page:current page/pp:number of items per page
# GET		get a VM 		http://host:port/api/v0.0/vminfos/<string:vm_id>
# POST		add a VM		http://host:port/api/v0.0/vminfos/<string:vm_id>
# PUT		update a VM		http://host:port/api/v0.0/vminfos/<string:vm_id>
# DELETE	delete a VM		http://host:port/api/v0.0/vminfos/<string:vm_id>

# all the imports
from flask_restful import reqparse, Resource, inputs
'''
    change by Shawn.T:
    from models import app, VirtualMachine, db
'''
from tecstack import db
from models import VirtualMachine
'''
    end
'''


# VMINFOList API
class VMINFOListAPI(Resource):

    # request parsing:
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # page
        self.reqparse.add_argument(
            'page', type=int, help='Page must be an integer')
        # pp: number of items per page
        self.reqparse.add_argument(
            'pp', type=int,
            help='PerPage must be an integer', dest='per_page')
        super(VMINFOListAPI, self).__init__()

    # get the VM list (paging done)
    def get(self):
        args = self.reqparse.parse_args()
        page = args['page']
        if not page:
            query = VirtualMachine.query.order_by(VirtualMachine.VM_ID).all()
            vms = [row.to_json() for row in query]
            return {'vm_infos': vms}, 200
        else:
            '''
                parameter verification 4 page
            '''
            if args['page'] <= 0:
                return {'error': 'Page must be positive'}, 400
            '''
                end
            '''
            per_page = args['per_page']
            if not per_page:
                # set default
                per_page = 20
            '''
                parameter verification 4 pp/per_page
            '''
            if args['per_page'] <= 0:
                return {'error': 'Per Page must be positive'}, 400
            '''
                end
            '''
            query = VirtualMachine.query.paginate(page, per_page, False)
            vms = [row.to_json() for row in query.items]
            return {'total_page': query.pages, 'vm_infos': vms}, 200


# VMINFO API : visit by unique vm_id
class VMINFOAPI(Resource):

    # request parsing
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'vm_id', type=str, help='VM_ID must be a string')
        self.reqparse.add_argument(
            'pm_id', type=str, help='PM_ID must be a string')
        self.reqparse.add_argument(
            'vm_name', type=str, help='VM_Name must be a string')
        '''
            basic format detection 4 IP
        '''
        self.reqparse.add_argument(
            'ip', type=inputs.regex(r'^(\d{1,3}\.){3}\d{1,3}$'),
            help='Not an IP')
        '''
            end
        '''
        self.reqparse.add_argument(
            'creater_time', type=str, help='Creater_Time must be a string')
        self.reqparse.add_argument(
            'vn_id', type=str, help='VN_ID must be a string')
        self.reqparse.add_argument(
            'vm_status', type=int, help='VM_STATUS must be an integer')
        super(VMINFOAPI, self).__init__()

    # get a single VM
    def get(self, vm_id):
        vm_info = VirtualMachine.query.filter_by(VM_ID=vm_id).first()
        if not vm_info:
            return {'error': 'VM %s Not Found' % vm_id}, 404
        return {'vm_info': vm_info.to_json()}, 200

    # add a new VM
    def post(self):
        try:
            args = self.reqparse.parse_args()
            vm_id = args['vm_id']
            if vm_id:
                old_vm = VirtualMachine.query.filter_by(VM_ID=vm_id).first()
                if not old_vm:
                    new_vm = VirtualMachine(
                        vm_id=vm_id, pm_id=args['pm_id'],
                        vm_name=args['vm_name'], ip=args['ip'],
                        creater_time=args['creater_time'],
                        vn_id=args['vn_id'], vm_status=args['vm_status'])
                    db.session.add(new_vm)
                    db.session.commit()
                    return {'vm_info': new_vm.to_json()}, 201
                else:
                    return {'error': 'VM %s Already Existed' % vm_id}, 403
            else:
                return {'error': 'VM_ID must be a string'}, 400
        except Exception as e:
            return {'error': e}, 500

    # delete a VM
    def delete(self, vm_id):
        try:
            old_vm = VirtualMachine.query.filter_by(VM_ID=vm_id).first()
            if old_vm:
                db.session.delete(old_vm)
                db.session.commit()
                return {}, 204
            else:
                return {'error': 'VM %s Not Found' % vm_id}, 404
        except Exception as e:
            return {'error': e}, 500

    # update a VM
    def put(self, vm_id):
        try:
            vm = VirtualMachine.query.filter_by(VM_ID=vm_id).first()
            if vm:
                args = self.reqparse.parse_args()
                pm_id = args['pm_id']
                if pm_id:
                    vm.PM_ID = pm_id
                vm_name = args['vm_name']
                if vm_name:
                    vm.VM_Name = vm_name
                ip = args['ip']
                if ip:
                    vm.IP = ip
                creater_time = args['creater_time']
                if creater_time:
                    vm.Creater_Time = creater_time
                vn_id = args['vn_id']
                if vn_id:
                    vm.VN_ID = vn_id
                vm_status = args['vm_status']
                if vm_status:
                    vm.VM_STATUS = vm_status
                db.session.commit()
                return {'vm_info': vm.to_json()}, 201
            else:
                return {'error': 'VM %s Not Found' % vm_id}, 404
        except Exception as e:
            return {'error': e}, 500
