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
        self._usermng = usermng()
        self._planmng = planlist()
        mthread.mthread.__init__(self,self.procdata,5000)
        self.__name =  'dataprocessthread'
        linfo(self.__name ,'create')
    def procdata(self,data):
        pack = datapack()
        pack.parsenetdata(data)
        print('type is %s'%pack.type)
        if pack.type == en_dp_type.connectstatus.name:
            _user = user()
            _user.parsfromdata(pack)
            self._usermng.add(_user)
            if _user.online == True:
                linfo('',_user.name+" online!")
            else:
                linfo('',_user.name+" offline!")
        elif pack.type == en_dp_type.workplan.name:
            element = XML(pack.body)
          #  print(pack.body)

            if element is None:
                lerror('','plan format is wrong')
                return
            print(len(element.getchildren()))
            for p in element.getchildren():
                _plan = plan()
                if _plan.parsexml(p)  == True:
                    self._planmng.processbytype(_plan)
#        linfo(self.__name ,'proc data ' + pack.formatxml())


