# empty __init__.py to make module VMINFO visible for IMPORTs

from tecstack import api
from services import VMINFOListAPI, VMINFOAPI, VMHELPAPI
from pmService import PMINFOListAPI, PMINFOAPI, PMHELPAPI


# VMINFO API
api.add_resource(
    VMINFOListAPI, '/api/v0.0/vminfos', endpoint='vminfos_ep')
api.add_resource(
    VMINFOAPI, '/api/v0.0/vminfos',
    endpoint='vminfo_pep')
api.add_resource(
    VMINFOAPI, '/api/v0.0/vminfos/<string:vm_id>',
    endpoint='vminfo_ep')
api.add_resource(
    VMHELPAPI, '/api/v0.0/vminfos/help/<string:vm_id>',
    endpoint='vmhelp_ep')

# PMINFO API
api.add_resource(
    PMINFOListAPI, '/api/v0.0/pminfos', endpoint='pminfos_ep')
api.add_resource(
    PMINFOAPI, '/api/v0.0/pminfos',
    endpoint='pminfo_pep')
api.add_resource(
    PMINFOAPI, '/api/v0.0/pminfos/<string:pm_id>',
    endpoint='pminfo_ep')
api.add_resource(
    PMHELPAPI, '/api/v0.0/pminfos/help/<string:pm_id>',
    endpoint='pmhelp_ep')
