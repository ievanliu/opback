# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: Leann Mak
# Email: leannmak@139.com
# Date: July 25, 2016
#
# This is the model module of eater package.

from .. import db, utils
from sqlalchemy.ext.declarative import declared_attr
import re


# default database bound
my_default_database = None


class Doraemon(db.Model):
    """
        Eater Super Model.
    """
    __abstract__ = True

    # tablename
    @declared_attr
    def __tablename__(cls):
        pattern = re.compile(r'([A-Z]+[a-z]+|^[A-Z]+[^A-Z]*$)')
        words = pattern.findall(cls.__name__)
        tname = ''
        if len(words) > 1:
            for w in words[:-1]:
                tname += '%s_' % w
        tname += words[-1]
        return tname.lower()

    # uuid
    @declared_attr
    def id(cls):
        return db.Column(
            db.String(64), primary_key=True,
            default=utils.genUuid(cls.__name__))

    # name list of base classes
    def bases(self):
        names = []
        for x in self.__class__.__bases__:
            names.append(x.__name__)
        return names

    # list of model columns
    def columns(self):
        return self.__class__.__mapper__.columns.__dict__['_data']

    # list of model relationships
    def relationships(self):
        return self.__class__.__mapper__.relationships.__dict__['_data']

    # constructor
    def __init__(self, **kw):
        if kw:
            cols, relations, isColComplete, isRelComplete = \
                self.checkColumnsAndRelations(**kw)
            if isColComplete:
                d = dict(cols, **relations)
                for k, w in d.items():
                    setattr(self, k, w)

    # for print
    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.id)

    # output columns and relationships to dict
    def to_dict(self, count=0):
        columns = self.columns()
        relationships = self.relationships()
        # get columns
        d = {k: getattr(self, k) for k in columns.keys()}
        # recursion ends (better limit count to be <= 3)
        # or it may risk to be maximum recursion depth exceeded
        if not relationships or count == 2:
            return d
        count += 1
        # get relationships
        for k in relationships.keys():
            relation = getattr(self, k)
            if relation:
                if hasattr(relation, '__iter__'):
                    d[k] = [x.to_dict(count)
                            for x in relation if hasattr(x, 'to_dict')]
                elif hasattr(relation, 'to_dict'):
                    d[k] = [relation.to_dict(count)]
            else:
                d[k] = []
        return d

    # find out params in table columns and relationships
    def checkColumnsAndRelations(self, **kw):
        cols, relations = {}, {}
        isColComplete, isRelComplete = True, True
        columns = self.columns()
        relationships = self.relationships()
        if kw:
            # check columns
            for k, w in columns.items():
                if k in kw.keys():
                    cols[k] = kw[k]
                elif not w.nullable and not w.default:
                    # non-nullable column which has no default value
                    # should not be left
                    isColComplete = False
            # check relationships
            for k, w in relationships.items():
                if (k in kw.keys()) and (w.secondary is not None):
                    # only many-to-many relationship
                    # can be initialized in this way
                    relations[k] = kw[k]
                elif w.secondary is not None:
                    # only many-to-many relationship
                    # should be initialized in this way
                    isRelComplete = False
        return cols, relations, isColComplete, isRelComplete

    # insert a record
    # input dict{}:
    # whole factors (except id, which is optional) of a new record
    # output dict{}: the inserted new record
    def insert(self, **kw):
        if kw:
            obj = self.__class__(**kw)
            db.session.add(obj)
            try:
                db.session.commit()
                return obj.to_dict()
            except:
                db.session.rollback()
        return None

    # update a record
    # input: str: id, dict{}: factors to update
    # output dict{}: the updated record
    def update(self, id, **kw):
        obj = self.__class__.query.filter_by(id=id).first()
        if obj:
            cols, relations, isColComplete, isRelComplete = \
                self.checkColumnsAndRelations(**kw)
            d = dict(cols, **relations)
            for k, w in d.items():
                setattr(obj, k, w)
            try:
                db.session.commit()
                return obj.to_dict()
            except:
                db.session.rollback()
        return None

    # get (a) record(s)
    # input dict{}: conditions for search
    # output json list[]: record(s) s.t. conditions
    def get(self, **kw):
        if kw:
            cols, relations, isColComplete, isRelComplete = \
                self.checkColumnsAndRelations(**kw)
            li = self.__class__.query.filter_by(**cols).all()
        else:
            li = self.__class__.query.all()
        if li:
            return [x.to_dict() for x in li]
        return None

    # delete a record
    # input str: id
    # output boolean: True if deleted, False if failed to delete
    def delete(self, id):
        old_rec = self.__class__.query.filter_by(id=id).first()
        if old_rec:
            db.session.delete(old_rec)
            try:
                db.session.commit()
                return True
            except:
                db.session.rollback()
        return False


"""
many-to-many relationships between OperatingSystem and OSUser
"""
user2os = db.Table(
    'user2os',
    db.Column('os_id', db.String(64), db.ForeignKey('operating_system.id')),
    db.Column('user_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


"""
many-to-many relationships between ITEquipment and OSUser
"""
osuser2it = db.Table(
    'osuser2it',
    db.Column('it_id', db.String(64), db.ForeignKey('itequipment.id')),
    db.Column('osuser_id', db.String(64), db.ForeignKey('osuser.id')),
    info={'bind_key': my_default_database}
)


class IP(Doraemon):
    """
        IP Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint(
            'ip_addr', 'ip_mask', 'ip_category',
            'if_id', 'it_id', name='_ip_uc'),)

    # IP address
    ip_addr = db.Column(db.String(64), unique=True)
    # IP mask
    ip_mask = db.Column(db.String(64))
    # IP category (vm/pm/network/security/storage/vip/unused)
    ip_category = db.Column(db.String(64), nullable=False)
    # interface which IP belongs to
    if_id = db.Column(db.String(32), db.ForeignKey('interface.id'))
    # IT equipment which IP belongs to
    it_id = db.Column(db.String(64), db.ForeignKey('itequipment.id'))


class Interface(Doraemon):
    """
        Interface Model.
    """
    __bind_key__ = my_default_database

    # interface name
    name = db.Column(db.String(64), unique=True)
    # IP
    ip = db.relationship('IP', backref='inf', lazy='dynamic')


class OperatingSystem(Doraemon):
    """
        Operating System Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('name', 'version', name='_os_uc'),)

    # OS name
    name = db.Column(db.String(64))
    # OS version
    version = db.Column(db.String(64))
    # IT equipment
    it = db.relationship(
        'ITEquipment', backref='os', lazy='dynamic')
    # OS user
    user = db.relationship(
        'OSUser', secondary='user2os', backref='os', lazy='dynamic')


class OSUser(Doraemon):
    """
        Operating System User Model.
        Set 'enable_typechecks=False' to enable subtype polymorphism.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint(
            'name', 'password', 'privilege', name='_osuser_uc'),)

    # OS user name
    name = db.Column(db.String(64))
    # OS user password
    password = db.Column(db.String(64))
    # OS user privilege
    privilege = db.Column(db.String(64))
    # IT equipment
    it = db.relationship(
        'ITEquipment', secondary='osuser2it',
        enable_typechecks=False, lazy='dynamic')


class Rack(Doraemon):
    """
        Rack Model.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('label', 'it_id', name='_rack_uc'),)

    # rack label
    label = db.Column(db.String(64), unique=True)
    # IT equipment which is installed in the rack
    it_id = db.Column(db.String(64), db.ForeignKey('itequipment.id'))


class ITEquipment(Doraemon):
    """
        IT Equipment Model.
        Superclass of Computer, Network, Storage and Security.
        Set 'enable_typechecks=False' to enable subtype polymorphism.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint(
            'label', 'name', 'setup_time', 'os_id', name='_it_uc'),)

    # IT equipment label
    label = db.Column(db.String(64), unique=True)
    # IT equipment host name
    name = db.Column(db.String(64), unique=True)
    # IT equipment setup time
    setup_time = db.Column(db.String(64))
    # operating system
    os_id = db.Column(db.String(32), db.ForeignKey('operating_system.id'))
    # OS user
    osuser = db.relationship(
        'OSUser', secondary='osuser2it',
        enable_typechecks=False, lazy='dynamic')
    # IT equipment IP
    ip = db.relationship(
        'IP', enable_typechecks=False, backref='it', lazy='dynamic')
    # IT equipment location
    rack = db.relationship(
        'Rack', enable_typechecks=False, backref='it', lazy='dynamic')


class Computer(ITEquipment):
    """
        Computer Model.
        Child of ITEquipment.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('spec_id', 'iqn_id', 'group_id', name='_com_uc'),)

    # use super class ITEquipment uuid as Computer uuid
    id = db.Column(
        db.String(64), db.ForeignKey('itequipment.id'),
        primary_key=True)
    # iscsi name
    iqn_id = db.Column(db.String(256), unique=True)
    # business group id
    group_id = db.Column(db.String(64))
    # computer specification
    spec_id = db.Column(
        db.String(64), db.ForeignKey('computer_specification.id'))


class ComputerSpecification(Doraemon):
    """
        Computer Specification Model.
    """
    __bind_key__ = my_default_database

    # each specification must be unique
    # which either insert() or update() is subject to
    __table_args__ = (
        db.UniqueConstraint(
            'cpu_fre', 'cpu_num', 'memory', 'disk', name='_spec_uc'),)

    # CPU main frequency
    cpu_fre = db.Column(db.String(64))
    # CPU number
    cpu_num = db.Column(db.Integer)
    # memory
    memory = db.Column(db.String(64))
    # hard disk size
    disk = db.Column(db.String(64))
    # IT equipment IP
    computer = db.relationship(
        'Computer', backref='spec', lazy='dynamic')


class PhysicalMachine(Computer):
    """
        Physical Machine Model.
        Child of Computer.
    """
    __bind_key__ = my_default_database

    # use super class Computer uuid as PysicalMachine uuid
    id = db.Column(
        db.String(64), db.ForeignKey('computer.id'),
        primary_key=True)
    # related virtual machines
    vm = db.relationship(
        'VirtualMachine',
        backref='pm',
        foreign_keys='VirtualMachine.pm_id',
        lazy='dynamic')


class VirtualMachine(Computer):
    """
        Virtual Machine Model.
        Child of Computer.
    """
    __bind_key__ = my_default_database
    __table_args__ = (
        db.UniqueConstraint('pm_id', 'vm_pid', name='_pm_vm_uc'),)

    # use super class Computer uuid as VirtualMachine uuid
    id = db.Column(
        db.String(64), db.ForeignKey('computer.id'),
        primary_key=True)
    # related pm
    pm_id = db.Column(
        db.String(64), db.ForeignKey('physical_machine.id'))
    # vm pid
    vm_pid = db.Column(db.String(64))
