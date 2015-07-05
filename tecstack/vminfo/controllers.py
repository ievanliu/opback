
from flask import request, jsonify
from tecstack import app

'''
    change by Leann Mak:
    append prefix 'vminfo' to avoid duplication
    2015/7/5
'''


@app.route('/vminfo')
def vminfo_index():
    app.logger.info('Got visit from %s.' % request.remote_addr)
    return "Hello vminfo!"


@app.route('/vminfo/_add_numbers')
def vminfo_add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
'''
    end
'''
