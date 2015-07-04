
from flask import request, jsonify
from tecstack import app


@app.route('/')
def index():
    app.logger.info('Got visit from %s.' % request.remote_addr)
    return "Hello vminfo!"


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
