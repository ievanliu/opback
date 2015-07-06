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
from flask_restful import reqparse, abort, Api, Resource
from model import app, Vm_info_tab, db
import logging

api = Api(app)

# VMINFOList API


class VMINFOListAPI(Resource):

    # request parsing:
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        # page
        self.reqparse.add_argument(
            'page', type=int, help='Page cannot be converted')
        # pp: number of items per page
        self.reqparse.add_argument(
            'pp', type=int,
            help='PerPage cannot be converted', dest='per_page')
        super(VMINFOListAPI, self).__init__()

    # get the VM list (paging done)
    def get(self):
        args = self.reqparse.parse_args()
        page = args['page']
        if not page:
            query = Vm_info_tab.query.order_by(Vm_info_tab.VM_ID).all()
            vms = [row.to_json() for row in query]
            return {'vm_infos': vms}
        else:
            per_page = args['per_page']
            if not per_page:
                # set default
                per_page = 20
            query = Vm_info_tab.query.paginate(page, per_page, False)
            vms = [row.to_json() for row in query.items]
            return {'total_page': query.pages, 'vm_infos': vms}

api.add_resource(VMINFOListAPI, '/api/v0.0/vminfos', endpoint='vminfos')


# VMINFO API : visit by unique vm_id
class VMINFOAPI(Resource):
    # request parsing

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'pm_id', type=str, help='PM_ID cannot be converted')
        self.reqparse.add_argument(
            'vm_name', type=str, help='VM_Name cannot be converted')
        self.reqparse.add_argument(
            'ip', type=str, help='IP cannot be converted')
        self.reqparse.add_argument(
            'creater_time', type=str, help='Creater_Time cannot be converted')
        self.reqparse.add_argument(
            'vn_id', type=str, help='VN_ID cannot be converted')
        self.reqparse.add_argument(
            'vm_status', type=int, help='VM_STATUS cannot be converted')
        super(VMINFOAPI, self).__init__()

    # get a single VM
    def get(self, vm_id):
        vm_info = Vm_info_tab.query.filter_by(VM_ID=vm_id).first()
        if not vm_info:
            abort(404, message='VM Not Found'.format(str))
        return {'vm_info': vm_info.to_json()}

    # add a new VM
    def post(self, vm_id):
        try:
            old_vm = Vm_info_tab.query.filter_by(VM_ID=vm_id).first()
            if not old_vm:
                args = self.reqparse.parse_args()
                new_vm = Vm_info_tab(vm_id=vm_id, pm_id=args['pm_id'],
                                     vm_name=args['vm_name'],
                                     ip=args['ip'], creater_time=args[
                                         'creater_time'],
                                     vn_id=args['vn_id'],
                                     vm_status=args['vm_status'])
                db.session.add(new_vm)
                db.session.commit()
                message = 'VM %s Successfully Added' % vm_id
                return {'message': message, 'vm_info': new_vm.to_json()}
            else:
                abort(
                    403, message=('VM %s Already Existed' % vm_id).format(str))
        except StandardError, e:
            logging.exception(e)
            abort(500, message='Server Error'.format(str))

    # delete a VM
    def delete(self, vm_id):
        try:
            old_vm = Vm_info_tab.query.filter_by(VM_ID=vm_id).first()
            if old_vm:
                db.session.delete(old_vm)
                db.session.commit()
                message = 'VM %s Successfully Deleted' % vm_id
                return {'message': message}
            else:
                abort(404, message='VM Not Found'.format(str))
        except StandardError, e:
            logging.exception(e)
            abort(500, message='Server Error'.format(str))

    # update a VM
    def put(self, vm_id):
        try:
            vm = Vm_info_tab.query.filter_by(VM_ID=vm_id).first()
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
                message = 'VM Info Successfully Updated'
                return {'message': message, 'vm_info': vm.to_json()}
            else:
                abort(404, message='VM Not Found'.format(str))
        except StandardError, e:
            logging.exception(e)
            abort(500, message='Server Error'.format(str))

api.add_resource(
    VMINFOAPI, '/api/v0.0/vminfos/<string:vm_id>', endpoint='vminfo')


if __name__ == '__main__':
    app.run(debug=True)
