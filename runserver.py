# -*- coding:utf-8 -*-
#
# Author: promisejohn
# Email: promise.john@gmail.com
#

from tecstack import app
from tecstack import controllers
'''
    add by Leann Mak
    2015/7/15
'''
import tecstack.vminfo.controllers as controllers_vminfo
'''
    end
'''


if __name__ == '__main__':
    print controllers
    print controllers_vminfo
    app.run(host='0.0.0.0', port=5000, debug=True)
