# -*- coding:utf-8 -*-
__author__ = 'tang'
from base.appdefine import *
from time import ctime
from datetime import datetime
import pickle
from base.mpath import mpath
import copy
__usermng_instance__ = None
__have_usermng_instance = False
class user():
    def __init__(self,name='',nickname='',ip='',online = False):
        self.name = name.strip()
        self.nickname = nickname.strip()
        self.ip = ip.strip()
        self.online = online
    """
    data = datapack
    """
    def parsfromdata(self,data):
        self.name = data.username
        self.nickname = data.nickname
        if data.type == en_dp_type.connectstatus.name:
            if data.body.upper() == constdef.OFFLINE:
                self.online = False
            else:
                self.online = True
        self.ip = data.ip
class usermng():
    def __init__(self):
        global __have_usermng_instance,__usermng_instance__
        if __usermng_instance__ != None:
            return
        self._userlist = []
        self.admin = None #本机用户
        self.savetime = datetime.now()
        __have_usermng_instance = True
    @staticmethod
    def instance():
        global __usermng_instance__
        if __usermng_instance__ == None:
            if os.path.exists(mpath.inistance().getconfigpath()+'user.dat') == False:
                __usermng_instance__ = usermng()
            else:
                with open(mpath.inistance().getconfigpath()+ 'user.dat','rb') as f:
                    __usermng_instance__ = pickle.load(f)
                f.close()
        return __usermng_instance__
    def setadmin(self,_user):
        user = copy.copy(_user)
        self.admin = user
    def getadmin(self):
        return self.admin
    def writetofile(self):
        self.savetime = datetime.now()
        global __usermng_instance__
        with open(mpath.inistance().getconfigpath()+'user.dat','wb') as f:
            pickle.dump(__usermng_instance__,f)
        f.close()

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
            for iu in self._userlist:
                if iu.name == user.name:
                    self._userlist[nIndex] = user
                    return
                nIndex +=1
        else:
            self._userlist.append(user)
    def remove(self,_user):
        user = copy.copy(_user)
        quser = self._query(user)
        if quser != None:
            self._userlist.remove(quser)
    def _query(self,_user):
        user = copy.copy(_user)
        for iu in self._userlist:
            if iu.name == user.name:
                return iu
        return None
    def querybyname(self,name):
        return self._query(user(name,'',''))
    def querybynickname(self,nickname):
        return self._query(user('',nickname,''))
    def querybyip(self,ip):
        return self._query(user('','',ip))
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