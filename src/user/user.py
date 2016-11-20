# -*- coding:utf-8 -*-
__author__ = 'tang'
from base.appdefine import *
from time import ctime
from datetime import datetime
import pickle
from base.mpath import mpath
from base.appdefine import ipaddress
import copy
from collections import defaultdict
__usermng_instance__ = None
__orgmng_instance__ = None

class user():
    def __init__(self,name='',nickname='',addr:ipaddress = None,online = False):
        self.name = name.strip()
        self.nickname = nickname.strip()
        self.addr = addr
        self.online = online
        self.email = ''
        self.datestamp = datetime.now().date()
    """
    data = datapack
    """
    def parsfromdata(self,data):
        self.name = data.username
        self.nickname = data.nickname
        parser = XML(data.body)

        if data.type == en_dp_type.connectstatus.name:
            if  parser.find('status').text  == constdef.OFFLINE:
                self.online = False
            else:
                self.online = True
            self.email = parser.find('email').text.strip()
            nport = int(parser.find('port').text)
            self.addr = ipaddress(data.ip,nport)
        self.timestamp = datetime.now()
class userlist():
    def __init__(self):
        self.userlist = []
    def isuserexist(self,_user):
        user = copy.copy(_user)
        if self._query(user) != None:
            return True
        else:
            return False
    def add(self,_user):
        user = copy.copy(_user)
        if self.isuserexist(user) == True:
            nIndex = 0
            for iu in self.userlist:
                if iu.name == user.name:
                    self.userlist[nIndex] = user
                    return
                nIndex +=1
        else:
            self.userlist.append(user)
    def remove(self,_user):
        user = copy.copy(_user)
        quser = self._query(user)
        if quser != None:
            self.userlist.remove(quser)
    def filtervalid(self):#这个函数只能在inistance函数内调用
        ul = [i for i in self.userlist if (datetime.now().date() - i.datestamp).days < 30]
        #30天内的用户信息是有效的
        for u in ul:
            u.online = False #初始化时都置为false
        self.userlist = ul
    def _query(self,_user):
        user = copy.copy(_user)
        for iu in self.userlist:
            if iu.name == user.name:
                return iu
        return None
    def querybyname(self,name):
        return self._query(user(name,'',''))
    def querybynickname(self,nickname):
        return self._query(user('',nickname,''))
    def querybyip(self,ip):
        return self._query(user('','',ip))
    def list(self):
        return self.userlist
class usermng(userlist):
    def __init__(self):
        global __usermng_instance__
        if __usermng_instance__ != None:
            return
        self._admin = None #本机用户
        self._path = 'user.dat'
        userlist.__init__(self)
    @staticmethod
    def instance():
        global __usermng_instance__
        if __usermng_instance__ == None:
            _path = 'user.dat'
            if os.path.exists(mpath.inistance().getconfigpath() + _path) == False:
                __usermng_instance__ = usermng()
            else:
                with open(mpath.inistance().getconfigpath()+ _path,'r+b') as f:
                    __usermng_instance__ = pickle.load(f)
                    __usermng_instance__.filtervalid()
                    pickle.dump(__usermng_instance__,f)
                    f.close()
        return __usermng_instance__

    def setadmin(self,_user):
        user = copy.copy(_user)
        self._admin = user
    def getadmin(self):
        return self._admin
    def writetofile(self):
        with open(mpath.inistance().getconfigpath()+self._path,'w+b') as f:
            pickle.dump(__usermng_instance__,f)
        f.close()
class org():
    def __init__(self,name = '',nickname = '',password = '',creator = ''):
        self.name = name
        self.nickname = nickname
        self.password = password
        self.creator = creator
        self.userlist = userlist()
class orgmng():
    def __init__(self):
        global __orgmng_instance__
        if __orgmng_instance__ != None:
            return
        self._orgmap = defaultdict()
        self._path = mpath.inistance().getdatapath()+ 'orgnization.dat'
    def map(self):
        return self._orgmap
    def addorg(self,org):
        self._orgmap[org.name] = org
        self.writetofile()
    def queryorg(self,orgname):
        if self._orgmap.get(orgname) is None:
            return None
        else:
            return self._orgmap[orgname]
    def adduser(self,orgname,_user):
        if self._orgmap.get(orgname) is None:
            return False
        else:
            self._orgmap[orgname].userlist.add(_user)
            self.writetofile()
            return True
    def removeuser(self,orgname,_user):
        if self._orgmap.get(orgname) is None:
            return False
        else:
            self._orgmap[orgname].userlist.remove(_user)
            self.writetofile()
            return True

    def getuserlist(self,orgname):
        if self._orgmap.get(orgname) is None:
            return None
        else:
            return self._orgmap[orgname].userlist

    @staticmethod
    def instance():
        _path = mpath.inistance().getdatapath()+ 'orgnization.dat'
        global  __orgmng_instance__
        if __orgmng_instance__ == None:
            __orgmng_instance__ = orgmng()
            if os.path.exists(_path)  == True:
                with open(_path,'rb') as f:
                    print(_path)
                    __orgmng_instance__._orgmap = pickle.load(f)
                    f.close()
        return __orgmng_instance__
    def writetofile(self):
        with open(self._path,'wb') as f:
            pickle.dump(self._orgmap,f)
            f.close()
def test():
    um = usermng()
    cuser = user()
    cuser.name = 'tang'
    cuser.online = True
    um.add(cuser)
    cuser.name ='li'
    um.add(cuser)
    cuser.name = 'zhao'
    um.setadmin(cuser)
    with open(r'c:\user.dat','wb') as f:
        pickle.dump(um,f)
    f.close()
    um.writetofile('')
    uu = usermng()
    uu.readfromfile('')
    with open(r'c:\userstatus.dat','rb') as fi:
        uu = pickle.load(fi)
    fi.close()
#test()