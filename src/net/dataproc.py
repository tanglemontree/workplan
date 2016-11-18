# -*- coding:utf-8 -*-
__author__ = 'tang'
from log import *
from base import datapack,en_dp_type,constdef,net_data,sys_para,mpath,ipaddress
from . import mthread,psocket
from time import sleep
from user import user,usermng,orgmng,org
from plan import plan,curplans,PLAN_REPORT,PLAN_REPLY
from xml.etree.ElementTree import XML,Element,SubElement,tostring
from collections import defaultdict
import pickle
import os
class dataproc(mthread.mthread):
    def __init__(self):
        mthread.mthread.__init__(self,self.procdata,5000)
        self.__name =  'dataprocessthread'
        linfo(self.__name ,'create')
        self._sendthd = None
        self._recvthd = None
        self._ip = psocket.getlocalip()
        self._sendplanmap = defaultdict(set) #计划发送字典，发送了但未收到回应的计划信息 {plan.id:user[]}
        self.readfailedplans()
    def setthread(self,recv,send):
        self._sendthd = send
        self._recvthd = recv
    def procdata(self,data):
        pack = datapack()
        pack.parsenetdata(data)

        if pack.type == en_dp_type.connectstatus.name:
            _user = user()
            _user.parsfromdata(pack)
            # if self._ip == pack.ip:
            #     return #自己发送的上线信息不处理
            if pack is None:
                return
            elif _user.name == usermng.instance().getadmin().name:
                lerror(self.__name ,str.format('IP地址({0})上的用户名和您的用户名({1})一样，请改名！',_user.addr.ip,_user.name))
            self.proclineinfo(pack,_user)
            self.sendfailedplan(_user)#将此用户未收到计划补发给他
            if _user.online == True:
                linfo(self.__name ,_user.name+" online!")
                if _user.addr.ip != self._ip:
                    self.sendlineinfo(_user.addr,True)
            else:
                linfo(self.__name ,_user.name+" offline!")
        elif pack.type == en_dp_type.workplan.name:
            self._processplan(pack)
    def _processplan(self,pack):
        element = XML(pack.body)
          #  print(pack.body)

        if element is None:
            lerror(self.__name ,'plan format is wrong')
            return
        _user = usermng.instance().querybyname(pack.username)
        if _user is None:
            return
        elements = []
        if element.tag == 'plan':
            elements.add(element)
        else:
            for p in element.getchildren():
                elements.add(p)
        for p in elements:
            _plan = plan()
            if _plan.parsexml(p) == True:
                if _plan.type == PLAN_REPORT:
                    localplan = curplans.instance().querybyid(p.id)
                    if localplan == None:
                        lwarn(self.name,'reciev plan report,but cannot find the plan in local!')
                        return
                    if pack.username != localplan.boss:
                        lwarn(self.name,'reciev plan report,but the reporter is not the plan boss!')
                        return
                    else:
                        localplan.addreport(_plan)
                        _plan = localplan
                elif _plan.type == PLAN_REPLY:
                    self._sendplanmap[_plan.id].discard(usermng.instance().querybyname(pack.username))
                    linfo(self.name,pack.nickname + '已收到计划:'+_plan.id)
                    self.writefailedplans()
                else:
                    if not _plan.isproducer(pack.username):
                        lerror(self.name,'{0} want to send a plan,but he is not the produrcer,reject!'.format(pack.username))
                        return
                curplans.instance().processbytype(_plan)
                curplans.instance().writetofile()
                if _plan.type != PLAN_REPLY:
                    self.sendplanreply(_plan,_user.addr)

    def sendfailedplan(self,onlineuser:user):
        for id in self._sendplanmap:
            plan = curplans.instance().querybyid(id)
            if plan is None:
                self._sendplanmap.pop(id)
            else:
                for u in self._sendplanmap[id]:
                    if u.name == onlineuser.nickname:
                        self._sendpack(u.addr,en_dp_type.workplan.name,plan.formatxml())
                        break

    def writefailedplans(self):
        with open(mpath.inistance().getdatapath() + 'failsendplan.dat','wb') as f:
            pickle.dump(self._sendplanmap,f)
            f.close()
    def readfailedplans(self):
        if os.path.exists(mpath.inistance().getdatapath()+'failsendplan.dat') == False:
            return
        with open(mpath.inistance().getdatapath() + 'failsendplan.dat','rb') as f:
            self._sendplanmap = pickle.load(f)
            f.close()

    def sendplans(self,plans):
        for plan in plans:
            users = set()
            u = usermng.instance().querybyname(plan.boss)
            if u == None:
                lwarn(self.name,plan.boss + " 此用户不在系统列表内，无法将计划发送给他!")
            else:
                users.add(u)
            for mate in plan.teammates:
                u = usermng.instance().querybyname(mate)
                if u == None:
                    lwarn(self.name,mate + " 此用户不在系统列表内，无法将计划发送给他!")
                else:
                    users.add(u)
            for iu in users:
                self._sendpack(iu.addr,en_dp_type.workplan.name,plan.formatxml())
            self._sendplanmap[plan.id] = self._sendplanmap[plan.id].union(users)
            self.writefailedplans()

    def _sendpack(self,addr,packtype,packxml):
        dpack = datapack(usermng.instance().getadmin().name,
                         usermng.instance().getadmin().nickname,
                         packtype,packxml)

        data = net_data(addr.ip,addr.port,dpack.formatxml().encode('utf-8'),False)
        if self._sendthd is not None:
            self._sendthd.write(data)
    def sendplanreply(self,plan,addr):
        reply = Element("plan")
        SubElement(reply,'id').text = plan.id
        SubElement(reply,'type').text = PLAN_REPLY
        self._sendpack(addr,en_dp_type.workplan.name,tostring(reply,'utf-8').decode('utf-8'))
    def proclineinfo(self,pack:datapack,_user:user):

        sxml = '<body>' + pack.body + '</body>'
        parser = XML(sxml)
        nport = int(parser.find('port').text)
        xorgs = parser.findall('orgname')
        if xorgs != None:
            for org in xorgs:
                orgmng.instance().adduser(org.text,_user)
        usermng.instance().add(_user)

    def sendlineinfo(self,addr:ipaddress,status):
        if usermng.instance().getadmin() == None:
            return
        top = Element('port')
        top.text = str(usermng.instance().getadmin().addr.port)
        ss = ''
        for org in orgmng.instance().map().keys():
            top = Element('orgname')
            top.text = org
            ss = ss + tostring(top,'utf-8').decode('utf-8')
        # TODO 遍历本地组织信息，形成orgname
        top = Element('status')
        top.text = constdef.ONLINE if status else constdef.OFFLINE
        ss = ss + tostring(top,'utf-8').decode('utf-8')
        self._sendpack(addr,en_dp_type.connectstatus.name,ss)
    def addorguser(self,orgname,username):
        org = orgmng.instance().queryorg(orgmng)
        _user = usermng.instance().querybyname(username)
        if _user is None:
            return
        top = Element('orginfo')
        top.set('orgname',org.name)
        top.set('orgnickname',org.nickname)
        top.set('type',constdef.ORG_ASKJION)
        child = SubElement(top,'password')
        child.text = org.password
        child = SubElement(top,'creator')
        child.text = org.creator

        self._sendpack(_user.addr,en_dp_type.orginfo.name,tostring(top,'utf-8').decode('utf-8'))
    def recvorginfo(self,dpack:datapack):
        parser = XML(dpack.body)
        top = parser.find('orginfo')
        if top is None:
            return
        neworg = org()
        neworg.name = top.get('orgname')
        neworg.nickname = top.get('nickname')
        if top.get('type') == constdef.ORG_ASKJION:
            neworg.password = top.get('password')
            neworg.creator = top.get('creator')
            print('do you want join ' + neworg.name +',yes of course')
            orgmng.instance().addorg(neworg)
            orgmng.instance().adduser(neworg.name,datapack.u)


