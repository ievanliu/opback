# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from tecstack import app
from tecstack import controllers

if __name__ == '__main__':
    print controllers
    app.run(host='0.0.0.0', port=5000, debug=True)
