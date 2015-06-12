# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#


from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello World! with DS"


@app.route('/_add_numbers')
def add_numbers():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a+b)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
