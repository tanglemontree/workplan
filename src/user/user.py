# -*- coding:utf-8 -*-
__author__ = 'tang'
from base.appdefine import *
from datetime import datetime
import pickle
from base.mpath import MPath
from socket import gethostname
from base.appdefine import IpAddress
import copy
import os
from collections import defaultdict
__user_mng_instance__ = None
__org_mng_instance__ = None


class User():
    def __init__(self,name='', nickname='', address: IpAddress=None, online=False):
        self.name = name.strip()
        self.nickname = nickname.strip()
        self.address = address  # ip and port
        self.online = online
        self.email = ''
        self.version = ''  #software version
        self.wechat = ''
        self.qq = ''
        self.unit = ''
        self.male = False
        self.officeaddress = ''
        self.privatephone = ''
        self.officephone = ''

        self.date_stamp = datetime.now().date()
    """
    data = datapack
    """
    def parse_data(self, data):
        self.name = data.username
        self.nickname = data.nickname
        parser = XML(data.body)

        if data.type == EnPackType.connectstatus.name:
            if parser.find('status').text == ConstDef.OFFLINE:
                self.online = False
            else:
                self.online = True
            self.email = parser.find('email').text.strip()
            nport = int(parser.find('port').text)
            self.address = IpAddress(data.ip, nport)
            self.version = parser.find('version')
            if parser.find('wechat') is not None:
                self.wechat = parser.find('wechat').text.strip()
            if parser.find('qq') is not None:
                self.qq = parser.find('qq').text.strip()
            if parser.find('officeaddress') is not None:
                self.officeaddress = parser.find('officeaddress').text.strip()
            if parser.find('privatephone') is not None:
                self.privatephone = parser.find('privatephone').text.strip()
            if parser.find('officephone') is not None:
                self.officephone = parser.find('officephone').text.strip()
            if parser.find('unit') is not None:
                self.unit = parser.find('unit').text.strip()
            if parser.find('sex') is not None:
                self.male = True if parser.find('sex').text.strip() == 'male' else False
        self.date_stamp = datetime.now()


def create_account():
        u = User()
        u.name = input("You need create your account.Please input your name:")
        if len(u.name.strip()) == 0:
            u.name = input("You need create your account.Please input your name:")
            if len(u.name.strip()) == 0:
                input('exit')
                return None
        u.nickname = input('please input your nickname:')
        if len(u.nickname.strip()) == 0:
            u.nickname = input("Please input your nickname:")
            if len(u.nickname.strip()) == 0:
                input('exit')
                return None
        u.name += gethostname()
        u.version = ConstDef.VERSION
        u.qq = '1223444'
        u.wechat = '1377823445'
        u.officephone = '010-82344'
        u.privatephone = '029-22222'
        u.male = False
        u.unit = 'PLC'
        u.officeaddress = 'tiananmen-5'
        return u


class UserList():
    def __init__(self):
        self.users = []
        
    def exist(self, _user):
        user = copy.copy(_user)
        if self._query(user) is not None:
            return True
        else:
            return False

    def add(self, _user):
        user = copy.copy(_user)
        if self.exist(user):
            nindex = 0
            for iu in self.users:
                if iu.name == user.name:
                    self.users[nindex] = user
                    return
                nindex += 1
        else:
            self.users.append(user)

    def remove(self, _user):
        user = copy.copy(_user)
        quser = self._query(user)
        if quser is not None:
            self.users.remove(quser)

    def filtervalid(self):  # 这个函数只能在inistance函数内调用
        ul = [i for i in self.users if (datetime.now().date() - i.date_stamp).days < 30]
        #  30天内的用户信息是有效的
        for u in ul:
            u.online = False   # 初始化时都置为false
        self.users = ul

    def _query(self, _user):
        user = copy.copy(_user)
        for iu in self.users:
            if iu.name == user.name:
                return iu
        return None

    def querybyname(self, name):
        return self._query(User(name, '', ''))

    def querybynickname(self, nickname):
        return self._query(User('', nickname, ''))

    def querybyip(self, ip):
        return self._query(User('', '', ip))

    def list(self):
        return self.users


class UserMng(UserList):
    def __init__(self):
        global __user_mng_instance__
        if __user_mng_instance__ is not None:
            return
        self._admin = None #本机用户
        self._path = 'user.dat'
        UserList.__init__(self)

    @staticmethod
    def instance():
        global __user_mng_instance__
        if __user_mng_instance__ is None:
            _path = 'user.dat'
            if not os.path.exists(MPath.instance().getconfigpath() + _path):
                __user_mng_instance__ = UserMng()
            else:
                with open(MPath.instance().getconfigpath() + _path, 'r+b') as f:
                    __user_mng_instance__ = pickle.load(f)
                    __user_mng_instance__.filtervalid()
                    pickle.dump(__user_mng_instance__, f)
                    f.close()
        return __user_mng_instance__

    def setadmin(self, _user):
        user = copy.copy(_user)
        self._admin = user

    def getadmin(self):
        return self._admin

    def writefile(self):
        with open(MPath.instance().getconfigpath()+self._path, 'w+b') as f:
            pickle.dump(__user_mng_instance__, f)
        f.close()


class Org():
    def __init__(self, name='', nickname='', password='', creator=''):
        self.name = name
        self.nickname = nickname
        self.password = password
        self.creator = creator
        self.users = UserList()


class OrgMng():
    def __init__(self):
        global __org_mng_instance__
        if __org_mng_instance__ is not None:
            return
        self._orgmap = defaultdict()
        self._path = MPath.instance().getdatapath() + 'organization.dat'

    def map(self):
        return self._orgmap

    def addorg(self, org):
        if len(org.users.list()) == 0:
            org.users.add(UserMng.instance().getadmin())
        self._orgmap[org.name] = org
        self.writefile()

    def queryorg(self, orgname):
        if self._orgmap.get(orgname) is None:
            return None
        else:
            return self._orgmap[orgname]

    def adduser(self, orgname, _user):
        if self._orgmap.get(orgname) is None:
            return False
        else:
            self._orgmap[orgname].users.add(_user)
            self.writefile()
            return True

    def removeuser(self, orgname, _user):
        if self._orgmap.get(orgname) is None:
            return False
        else:
            self._orgmap[orgname].users.remove(_user)
            self.writefile()
            return True

    def getuserlist(self, orgname):
        if self._orgmap.get(orgname) is None:
            return None
        else:
            return self._orgmap[orgname].users

    @staticmethod
    def instance():
        _path = MPath.instance().getdatapath() + 'organization.dat'
        global __org_mng_instance__
        if __org_mng_instance__ is None:
            __org_mng_instance__ = OrgMng()
            if os.path.exists(_path):
                with open(_path, 'rb') as f:
                    print(_path)
                    __org_mng_instance__._orgmap = pickle.load(f)
                    f.close()
        return __org_mng_instance__

    def writefile(self):
        with open(self._path, 'wb') as f:
            pickle.dump(self._orgmap,f)
            f.close()
def test():
    um = UserMng()
    cuser = User()
    cuser.name = 'tang'
    cuser.online = True
    um.add(cuser)
    cuser.name = 'li'
    um.add(cuser)
    cuser.name = 'zhao'
    um.setadmin(cuser)
    with open(r'c:\user.dat', 'wb') as f:
        pickle.dump(um, f)
    f.close()
    um.writefile('')
    uu = UserMng()
    uu.readfromfile('')
    with open(r'c:\userstatus.dat','rb') as fi:
        uu = pickle.load(fi)
    fi.close()
#test()