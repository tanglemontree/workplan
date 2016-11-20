# -*- coding:utf-8 -*-
__author__ = 'tang'
from log import *
from base import datapack,en_dp_type,constdef,net_data,sys_para,mpath,ipaddress
from . import mthread,psocket
from time import sleep
from user import user,usermng,orgmng,org
from plan import plan,curplans,PLAN_REPORT,PLAN_REPLY,totalplans
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
        self._ip = psocket.getlocalip()
        self._sendplanmap = defaultdict(set) #计划发送字典，发送了但未收到回应的计划信息 {plan.id:user[]}
        self.readfailedplans()
    def setthread(self,send):
        self._sendthd = send

    def procdata(self,data):
        pack = datapack()
        pack.parsenetdata(data)

        if pack.type == en_dp_type.connectstatus.name:
            _user = user()
            _user.parsfromdata(pack)
            if self._ip == pack.ip and _user.addr.port == usermng.instance().getadmin().addr.port:
             #   print('自己发送的上线信息不处理')
                return #自己发送的上线信息不处理
            if pack is None:
                return
            elif _user.name == usermng.instance().getadmin().name:
                lerror(self.__name ,str.format('IP地址({0})上的用户名和您的用户名({1})一样，请改名！',_user.addr.ip,_user.name))
            isreply = self.proclineinfo(pack,_user)
            self.sendfailedplan(_user)#将此用户未收到计划补发给他
            if _user.online == True:
                linfo(self.__name ,_user.name+" online!")
                if isreply == False:#不是对方发送的上线回答信息(广播信息),则发送回复上线信息
                    self.sendlineinfo(_user.addr,True,True)
            else:
                linfo(self.__name ,_user.name+" offline!")
        elif pack.type == en_dp_type.workplan.name:
            self._processplan(pack)
        elif pack.type == en_dp_type.orginfo.name:
            self._recvorginfo(pack)
    def _processplan(self,pack):
        top = XML(pack.body)
        print('plan:  ' + pack.body)
        _user = usermng.instance().querybyname(pack.username)
        if _user is None:
            return
        element = top.find('plans')
        subelment = []
        for p in element.getchildren():
            subelment.append(p)
        replyplans = []
        for p in subelment:
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
                # else:
                #     if not _plan.isproducer(pack.username):
                #         lerror(self.name,'{0} want to send a plan,but he is not the produrcer,reject!'.format(pack.username))
                #         return
                curplans.instance().processbytype(_plan)
                if _plan.type != PLAN_REPLY:
                    replyplans.append(_plan)
        curplans.instance().writetofile()
        self.sendplanreply(replyplans,_user.addr)
    def sendplanstouser(self,plans,ip:ipaddress):
        top = Element('body')
        child = SubElement(top,"plans")
        if len(plans) == 0:
            return
        for plan in plans:
            child.append(XML(plan.formatxml()))
        self._sendpack(ip,en_dp_type.workplan.name,tostring(top,'utf-8').decode('utf-8'))
        print("send plans->ip:" +ip.ip+"  " + str(ip.port)+ "  " +tostring(top,'utf-8').decode('utf-8'))
    def sendplans(self,plans):
        userplanmap = defaultdict(set)
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
                userplanmap[iu.name].add(plan)
            self._sendplanmap[plan.id] = self._sendplanmap[plan.id].union(users)

        for iu in userplanmap.keys():
            addr = usermng.instance().querybyname(iu).addr
            self.sendplanstouser(userplanmap[iu],addr)
        self.writefailedplans()
    def sendplanreply(self,plans,addr):
        if len(plans) == 0:
            return
        top = Element('body')
        replys = SubElement(top,"plans")
        for pl in plans:
            reply = SubElement(replys,'plan')
            SubElement(reply,'id').text = pl.id
            SubElement(reply,'type').text = PLAN_REPLY
        self._sendpack(addr,en_dp_type.workplan.name,tostring(top,'utf-8').decode('utf-8'))
    def sendfailedplan(self,onlineuser:user):
        userplans= []
        for id in self._sendplanmap:
            plan = totalplans.instance().querybyid(id)
            if plan is None:
                self._sendplanmap.pop(id)
            else:
                for u in self._sendplanmap[id]:
                    if u.name == onlineuser.name:
                        userplans.append(plan)
                        break
        self.sendplanstouser(userplans,onlineuser.addr)
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

    def _sendpack(self,addr,packtype,packxml):
        dpack = datapack(usermng.instance().getadmin().name,
                         usermng.instance().getadmin().nickname,
                         packtype,packxml)

        data = net_data(addr.ip,addr.port,dpack.formatxml().encode('utf-8'),False)
        if self._sendthd is not None:
            self._sendthd.write(data)

    def proclineinfo(self,pack:datapack,_user:user):
        parser = XML(pack.body)
        isreply = True if parser.find('isreply').text.strip().lower() == 'true' else False
        xorgs = parser.findall('orgname')
        if xorgs != None:
            for org in xorgs:
                orgmng.instance().adduser(org.text,_user)
        usermng.instance().add(_user)
        return isreply

    def sendlineinfo(self,addr:ipaddress,status,isreply):
        top = Element('body')
        if usermng.instance().getadmin() == None:
            return
        SubElement(top,'port').text = str(usermng.instance().getadmin().addr.port)
        SubElement(top,'status').text = constdef.ONLINE if status else constdef.OFFLINE
        if len(usermng.instance().getadmin().email) == 0:
            SubElement(top,'email').text = 'XXX'
        else:
            SubElement(top,'email').text = usermng.instance().getadmin().email
        SubElement(top,'isreply').text = 'true' if isreply else 'false'
        for org in orgmng.instance().map().keys():
            SubElement(top,'orgname').text =org
        # TODO 遍历本地组织信息，形成orgname
        ss = tostring(top,'utf-8').decode('utf-8')
        self._sendpack(addr,en_dp_type.connectstatus.name,ss)
        print("send " +addr.ip+"  " + str(addr.port)+ "  " + ss)
    def addorguser(self,orgname,username):
        neworg = orgmng.instance().queryorg(orgname)
        _user = usermng.instance().querybyname(username)

        if neworg is None or _user is None:
            return
        parser = Element('body')
        top = SubElement(parser,'orginfo')
        top.set('orgname',neworg.name)
        top.set('orgnickname',neworg.nickname)
        top.set('type',constdef.ORG_ASKJION)
        child = SubElement(top,'password')
        child.text = neworg.password
        child = SubElement(top,'creator')
        child.text = neworg.creator
        self._sendpack(_user.addr,en_dp_type.orginfo.name,tostring(parser,'utf-8').decode('utf-8'))

    def _recvorginfo(self,dpack:datapack):
        print('recive orginfo ' + dpack.formatxml())
        parser = XML(dpack.body)
        top = parser.find('orginfo')
        neworg = org()
        neworg.name = top.get('orgname')
        neworg.nickname = top.get('nickname')
        if top.get('type') == constdef.ORG_ASKJION:
            neworg.password = top.get('password')
            neworg.creator = top.get('creator')
            print('do you want join ' + neworg.name +',yes of course')
            orgmng.instance().addorg(neworg)
            _user = user()
            _user.parsfromdata(dpack)
            orgmng.instance().adduser(neworg.name,_user)
            self.sendlineinfo(ipaddress(sys_para.NET_GROUPADDR,sys_para.NET_GROUPRPORT),True,False)


