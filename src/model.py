#coding:utf-8
#BY Daisheng
#Jun,27,2015
#说明：
#1.按照vm_info_tab与publicip_tab两张表做模型，可关联字段为vm_info_tab.IP与
#publicip_tab.binding_PublicIP_LocalIP
#2.由于内网IP表有几十万条数据，不做导入
#3.下周添加pm_info_tab表（物理主机信息表）

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/share/helwldv001/test.db'
db = SQLAlchemy(app)
db.init_app(app)


class Vm_info_tab(db.Model):
    __tablename__ = 'vm_info_tab'
    #虚拟机ID
    VM_ID = db.Column(db.VARCHAR(length=64), primary_key=True)
    #物理机ID
    PM_ID = db.Column(db.VARCHAR(length=64))
    #虚拟机名称
    VM_Name = db.Column(db.VARCHAR(length=64))
    #虚拟机内网IP
    IP = db.Column(db.VARCHAR(length=32))
    #虚拟机创建时间
    Creater_Time = db.Column(db.VARCHAR(length=14))
    #子网ID
    VN_ID = db.Column(db.VARCHAR(length=32))
    #虚拟机状态：0-创建中，1-运行中
    VM_STATUS = db.Column(db.INT)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<VMname %r>' % self.VM_Name

    # def to_json(self):
    #     return {
    #         'id': self.id,
    #         'username': self.username,
    #         'email': self.email
    #     }


class Publicip_tab(db.Model):
    __tablename__ = 'publicip_tab'
    #公网IP ID
    Local_ID = db.Column(db.VARCHAR(length=50), primary_key=True)
    #公网IP
    IP = db.Column(db.VARCHAR(length=150), nullable=False)
    #公网IP状态：0：空闲，1：占用，2：未绑定, 5：弃用
    IP_Status = db.Column(db.VARCHAR(length=1), nullable=False)
    #对应的内网IP
    Binding_PublicIP_LocalIP = db.Column(db.VARCHAR(length=150))
    #申请时间
    Prop_Time = db.Column(db.VARCHAR(length=14))
    #操作时间
    operate_time = db.Column(db.INT)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<VMname %r>' % self.VM_Name

    # def to_json(self):
    #     return {
    #         'id': self.id,
    #         'username': self.username,
    #         'email': self.email
    #     }

def init_db(db):
    db.drop_all()
    db.create_all()
    #导入数据：sqlite3 <path to **.db> < data.sql
    #暂时先这种办法，等我改进

    # with app.open_resource('data.sql') as f:
    #     db.cursor().executescript(f.read())
   