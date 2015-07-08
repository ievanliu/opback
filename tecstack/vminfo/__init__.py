# empty __init__.py to make module VMINFO visible for IMPORTs

'''
    add by Leann Mak
    2015/7/8
'''
from tecstack import api
from services import VMINFOListAPI, VMINFOAPI

api.add_resource(
    VMINFOListAPI, '/api/v0.0/vminfos', endpoint='vminfos_ep')
api.add_resource(
    VMINFOAPI, '/api/v0.0/vminfos',
    endpoint='vminfo_pep')
api.add_resource(
    VMINFOAPI, '/api/v0.0/vminfos/<string:vm_id>',
    endpoint='vminfo_ep')
'''
    end
'''
