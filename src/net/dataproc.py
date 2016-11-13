# -*- coding:utf-8 -*-
__author__ = 'tang'
from log import *
from base import datapack,en_dp_type,constdef
from . import mthread
from time import sleep
from user import user,usermng
from plan import plan,planlist
from xml.etree.ElementTree import XML
class dataproc(mthread.mthread):
    def __init__(self):
        self._planmng = planlist()
        mthread.mthread.__init__(self,self.procdata,5000)
        self.__name =  'dataprocessthread'
        linfo(self.__name ,'create')
        self._sendthd = None
        self._recvthd = None
    def setthread(self,recv,send):
        self._sendthd = send
        self._recvthd = recv
    def procdata(self,data):
        pack = datapack()
        pack.parsenetdata(data)
        print('type is %s'%pack.type)
        if pack.type == en_dp_type.connectstatus.name:
            _user = user()
            _user.parsfromdata(pack)
            if _user == usermng.instance().getadmin():
                return #自己发送的上线信息不处理
            elif _user.name == usermng.instance().getadmin().name:
                lerror(self.__name ,str.format('用户名和IP地址为{0}一样，请改名！',_user.name))
            usermng.instance().add(_user)#更新用户信息
            if _user.online == True:
                linfo(self.__name ,_user.name+" online!")
                self.sendonlineinfo(_user.ip)
            else:
                linfo(self.__name ,_user.name+" offline!")
        elif pack.type == en_dp_type.workplan.name:
            element = XML(pack.body)
          #  print(pack.body)

            if element is None:
                lerror(self.__name ,'plan format is wrong')
                return
            #print(len(element.getchildren()))
            for p in element.getchildren():
                _plan = plan()
                if _plan.parsexml(p)  == True:
                    self._planmng.processbytype(_plan)
    def sendonlineinfo(self,ip):
        dpack = datapack(username = usermng.instance().getadmin().name,
                         nickname = usermng.instance().getadmin().nickname,
                         type = en_dp_type.connectstatus.name,constdef.ONLINE)
        data = net_data(ip,sys_para.NET_DESTPORT,dpack.formatxml().decode('utf-8'),False)
        if self._sendthd is not None:
            self._sendthd.write(data)




