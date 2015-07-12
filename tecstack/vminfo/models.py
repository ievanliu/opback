# coding:utf-8
# BY Daisheng
# Jul,02,2015

# from flask import Flask
# from flask.ext.sqlalchemy import SQLAlchemy
# from tecstack import app, db
from tecstack import db

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/\
# share/helwldv001/data/test.db'
# app.config['DTATBASE_FILE'] = '/home/share/helwldv001/dat\
# a/test.db'
# app.config['DATA_SOURCEFILE'] = '/home/share/helwldv001/d\
# ata/data0702/data0702.sql'
# db = SQLAlchemy(app)
# db.init_app(app)


'''
    物理机信息模型
'''


class PhysicalMachine(db.Model):
    __tablename__ = 'pm_info_tab'
    # 物理机ID
    PM_ID = db.Column(db.VARCHAR(length=64), primary_key=True)
    # 物理机名称
    PM_Name = db.Column(db.VARCHAR(length=64))
    '''
        add ForeignKey by leannmak
        2015/7/12
    '''
    # 物理机内网IP
    IP = db.Column(db.VARCHAR(length=32),
                   db.ForeignKey('publicip_tab.Binding_PublicIP_LocalIP'))
    '''
        end
    '''
    # 物理机创建时间
    Creat_Time = db.Column(db.VARCHAR(length=14))
    # iscsi连接名
    iscsiName = db.Column(db.VARCHAR(length=256))

    vm_info = db.relationship('VirtualMachine', backref='pm',
                              lazy='dynamic')

    def __init__(self, pm_id, pm_name, ip, creat_time,
                 iscsi_name):
        self.PM_ID = pm_id
        self.PM_Name = pm_name
        self.IP = ip
        self.Creat_Time = creat_time
        self.iscsiName = iscsi_name

    def __repr__(self):
        return '<PMname %r>' % self.PM_Name

    def to_json(self):
        return {
            'pm_id': self.PM_ID,
            'pm_name': self.PM_Name,
            'ip': self.IP,
            'creat_time': self.Creat_Time,
            'iscsi_name': self.iscsiName
        }


'''
    虚拟机信息模型
'''


class VirtualMachine(db.Model):
    __tablename__ = 'vm_info_tab'
    # 虚拟机ID
    VM_ID = db.Column(db.VARCHAR(length=64), primary_key=True)
    # 物理机ID
    PM_ID = db.Column(db.VARCHAR(length=64),
                      db.ForeignKey('pm_info_tab.PM_ID'))
    # 虚拟机名称
    VM_Name = db.Column(db.VARCHAR(length=64))
    '''
        add ForeignKey by leannmak
        2015/7/12
    '''
    # 虚拟机内网IP
    IP = db.Column(db.VARCHAR(length=32),
                   db.ForeignKey('publicip_tab.Binding_PublicIP_LocalIP'))
    '''
        end
    '''
    # 虚拟机创建时间
    Creater_Time = db.Column(db.VARCHAR(length=14))
    # 子网ID
    VN_ID = db.Column(db.VARCHAR(length=32))
    # 虚拟机状态：0-创建中，1-运行中
    VM_STATUS = db.Column(db.INT)

    def __init__(self, vm_id, pm_id, vm_name, ip, creater_time,
                 vn_id, vm_status):
        self.VM_ID = vm_id
        self.PM_ID = pm_id
        self.VM_Name = vm_name
        self.IP = ip
        self.Creater_Time = creater_time
        self.VN_ID = vn_id
        self.VM_STATUS = vm_status

    def __repr__(self):
        return '<VMname %r>' % self.VM_Name

    def to_json(self):
        return {
            'vm_id': self.VM_ID,
            'pm_id': self.PM_ID,
            'vm_name': self.VM_Name,
            'ip': self.IP,
            'creater_time': self.Creater_Time,
            'vn_id': self.VN_ID,
            'vm_status': self.VM_STATUS
        }


'''
    公网IP信息模型
'''


class PublicIP(db.Model):
    __tablename__ = 'publicip_tab'
    # 公网IP ID
    Local_ID = db.Column(db.VARCHAR(length=50), primary_key=True)
    # 公网IP
    IP = db.Column(db.VARCHAR(length=150), nullable=False)
    # 公网IP状态：0：空闲，1：占用，2：未绑定, 5：弃用
    IP_Status = db.Column(db.VARCHAR(length=1), nullable=False)
    # 对应的内网IP
    Binding_PublicIP_LocalIP = db.Column(db.VARCHAR(length=150))
    # 申请时间
    Prop_Time = db.Column(db.VARCHAR(length=14))
    # 操作时间
    operate_time = db.Column(db.INT)
    '''
        add by leannmak
        2015/7/12
    '''
    vm_info = db.relationship('VirtualMachine', backref='pub',
                              lazy='dynamic')
    pm_info = db.relationship('PhysicalMachine', backref='pub',
                              lazy='dynamic')
    '''
        end
    '''

    def __init__(self, local_id, ip, ip_status,
                 binding_publicip_localip, prop_time,
                 operate_time):
        self.Local_ID = local_id
        self.IP = ip
        self.IP_Status = ip_status
        self.Binding_PublicIP_LocalIP = binding_publicip_localip
        self.Prop_Time = prop_time
        self.operate_time = operate_time

    def __repr__(self):
        return '<Public IP %r>' % self.IP

    def to_json(self):
        return {
            'local_id': self.Local_ID,
            'ip': self.IP,
            'ip_status': self.IP_Status,
            'bingding_publicip_localip': self.Binding_PublicIP_LocalIP,
            'prop_time': self.Prop_Time,
            'operate_time': self.operate_time
        }


# '''
#     初始化数据库
# '''
# 创建数据库


# def init_db():
    # # db.drop_all()
    # db.create_all()


# # 导入数据


# def import_data():
    # import os
    # db_path = os.path.join(app.config['DB_FOLDER'],app.config['DB_FILE'])
    # print db_path
    # from sqlite3 import dbapi2 as sqlite3
    # rv = sqlite3.connect('D:\\Codes\\Python\\opback\\.data\\app.db')
    # rv.row_factory = sqlite3.Row
    # with app.open_resource('data0702.sql', mode='r') as f:
        # rv.cursor().executescript(f.read())
    # rv.commit()
    # rv.close()

# init_db()
# # import_data()
