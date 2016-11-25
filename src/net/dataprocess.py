# -*- coding:utf-8 -*-
__author__ = 'tang'
from log import *
from base import (DataPack, EnPackType, ConstDef, NetData, Sys_Para,
                  MPath, IpAddress)
from . import mthread, psocket
from user import User, UserMng, OrgMng, Org
from plan import Plan, CurPlans, PLAN_REPORT, PLAN_REPLY, TotalPlans
from xml.etree.ElementTree import XML, Element, SubElement, tostring
from collections import defaultdict
import pickle
import os


class DataProcess(mthread.MThread):
    def __init__(self):
        mthread.MThread.__init__(self, self.procdata, 5000)
        self.__name = '数据处理线程'
        linfo(self.__name, 'create')
        self._sendthd = None
        self._ip = psocket.getlocalip()
        self._sendplanmap = defaultdict(set)   # 计划发送字典，发送了但未收到回应的计划信息 {plan.id:user[]}
        self.readfailedplans()

    def setthread(self, send):
        self._sendthd = send

    def procdata(self, data):
        pack = DataPack()
        pack.parsenetdata(data)

        if pack.type == EnPackType.connectstatus.name:
            _user = User()
            _user.parse_data(pack)
            if self._ip == pack.ip and _user.address.port == UserMng.instance().getadmin().address.port:
                # print('自己发送的上线信息不处理')
                return
            if pack is None:
                return
            elif _user.name == UserMng.instance().getadmin().name:
                lerror(self.__name, str.format('IP地址({0})上的用户名和您的用户名({1})一样，请改名！',
                                               _user.address.ip, _user.name))
            isreply = self.proclineinfo(pack, _user)
            self.sendfailedplan(_user)  # 将此用户未收到计划补发给他
            if _user.online:
                linfo(self.__name, _user.name+" online!")
                if not isreply:  # 不是对方发送的上线回答信息(广播信息),则发送回复上线信息
                    self.sendlineinfo(_user.address, True, True)
            else:
                linfo(self.__name, _user.name+" offline!")
        elif pack.type == EnPackType.workplan.name:
            self._processplan(pack)
        elif pack.type == EnPackType.orginfo.name:
            self._recvorginfo(pack)

    def _processplan(self, pack):
        top = XML(pack.body)
        print('plan:  ' + pack.body)
        _user = UserMng.instance().querybyname(pack.username)
        if _user is None:
            return
        element = top.find('plans')
        subelment = []
        for p in element.getchildren():
            subelment.append(p)
        replyplans = []
        for p in subelment:
            _plan = Plan()
            if _plan.parsexml(p):
                if _plan.type == PLAN_REPORT:
                    localplan = CurPlans.instance().querybyid(p.id)
                    if localplan is None:
                        lwarn(self.name, 'reciev plan report,but cannot find the plan in local!')
                        return
                    if pack.username != localplan.boss:
                        lwarn(self.name, 'reciev plan report,but the reporter is not the plan boss!')
                        return
                    else:
                        localplan.addresseport(_plan)
                        _plan = localplan
                elif _plan.type == PLAN_REPLY:
                    self._sendplanmap[_plan.id].discard(UserMng.instance().querybyname(pack.username))
                    linfo(self.name, pack.nickname + '已收到计划:'+_plan.id)
                    self.writefailedplans()
                # else:
                #     if not _plan.isproducer(pack.username):
                #         lerror(self.name,'{0} want to send a plan,but he is not the produrcer,reject!'.format(pack.username))
                #         return
                CurPlans.instance().processbytype(_plan)
                if _plan.type != PLAN_REPLY:
                    replyplans.append(_plan)
        CurPlans.instance().writefile()
        self.sendplanreply(replyplans, _user.address)

    def sendplanstouser(self, plans, ip: IpAddress):
        top = Element('body')
        child = SubElement(top, "plans")
        if len(plans) == 0:
            return
        for plan in plans:
            child.append(XML(plan.formatxml()))
        self._sendpack(ip, EnPackType.workplan.name, tostring(top, 'utf-8').decode('utf-8'))
        print("send plans->ip:" +ip.ip+"  " + str(ip.port)+"  "+tostring(top, 'utf-8').decode('utf-8'))

    def sendplans(self, plans):
        userplanmap = defaultdict(set)
        for plan in plans:
            users = set()
            u = UserMng.instance().querybyname(plan.boss)
            if u is None:
                lwarn(self.name, plan.boss + " 此用户不在系统列表内，无法将计划发送给他!")
            else:
                users.add(u)
            for mate in plan.teammates:
                u = UserMng.instance().querybyname(mate)
                if u is None:
                    lwarn(self.name, mate + " 此用户不在系统列表内，无法将计划发送给他!")
                else:
                    users.add(u)
            for iu in users:
                userplanmap[iu.name].add(plan)
            self._sendplanmap[plan.id] = self._sendplanmap[plan.id].union(users)

        for iu in userplanmap.keys():
            address = UserMng.instance().querybyname(iu).address
            self.sendplanstouser(userplanmap[iu], address)
        self.writefailedplans()

    def sendplanreply(self, plans, addr: IpAddress):
        if len(plans) == 0:
            return
        top = Element('body')
        replys = SubElement(top, "plans")
        for pl in plans:
            reply = SubElement(replys, 'plan')
            SubElement(reply, 'id').text = pl.id
            SubElement(reply, 'type').text = PLAN_REPLY
        self._sendpack(addr, EnPackType.workplan.name, tostring(top, 'utf-8').decode('utf-8'))

    def sendfailedplan(self, onlineuser: User):
        userplans= []
        for id in self._sendplanmap:
            plan = TotalPlans.instance().querybyid(id)
            if plan is None:
                self._sendplanmap.pop(id)
            else:
                for u in self._sendplanmap[id]:
                    if u.name == onlineuser.name:
                        userplans.append(plan)
                        break
        self.sendplanstouser(userplans, onlineuser.address)

    def writefailedplans(self):
        with open(MPath.instance().getdatapath() + 'failsendplan.dat', 'wb') as f:
            pickle.dump(self._sendplanmap, f)
            f.close()

    def readfailedplans(self):
        if not os.path.exists(MPath.instance().getdatapath()+'failsendplan.dat'):
            return
        with open(MPath.instance().getdatapath() + 'failsendplan.dat', 'rb') as f:
            self._sendplanmap = pickle.load(f)
            f.close()

    def _sendpack(self, addr: IpAddress, packtype, packxml):
        dpack = DataPack(UserMng.instance().getadmin().name,
                         UserMng.instance().getadmin().nickname,
                         packtype, packxml)

        data = NetData(addr.ip, addr.port, dpack.formatxml().encode('utf-8'), False)
        if self._sendthd is not None:
            self._sendthd.write(data)

    def proclineinfo(self, pack: DataPack, _user: User):
        parser = XML(pack.body)
        isreply = True if parser.find('isreply').text.strip().lower() == 'true' else False
        xorgs = parser.findall('orgname')
        if xorgs is not None:
            for org in xorgs:
                OrgMng.instance().add_user(org.text, _user)
        UserMng.instance().add(_user)
        return isreply

    def sendlineinfo(self, addr: IpAddress, status, isreply):
        top = Element('body')
        administrator = UserMng.instance().getadmin()
        if administrator is None:
            return
        SubElement(top, 'port').text = str(administrator.address.port)
        SubElement(top, 'status').text = ConstDef.ONLINE if status else ConstDef.OFFLINE
        if len(administrator.email) == 0:
            SubElement(top, 'email').text = 'XXX'
        else:
            SubElement(top, 'email').text = administrator.email
        SubElement(top, 'isreply').text = 'true' if isreply else 'false'

        def setsubelment(tag, value):
            nonlocal top
            if len(value) > 0:
                SubElement(top, tag).text = value
        setsubelment('version', administrator.version)
        setsubelment('qq', administrator.qq)
        setsubelment('wechat', administrator.wechat)
        setsubelment('unit', administrator.unit)
        setsubelment('sex', ('male' if administrator.male else 'female'))
        setsubelment('officeaddress', administrator.officeaddress)
        setsubelment('privatephone', administrator.privatephone)
        setsubelment('officephone', administrator.officephone)
        for org in OrgMng.instance().map().keys():
            SubElement(top, 'orgname').text = org
        # TODO 遍历本地组织信息，形成orgname
        ss = tostring(top, 'utf-8').decode('utf-8')
        self._sendpack(addr, EnPackType.connectstatus.name, ss)
        print("send " + addr.ip+"  " + str(addr.port)+"  " + ss)

    def addorguser(self, orgname, username):
        neworg = OrgMng.instance().queryorg(orgname)
        _user = UserMng.instance().querybyname(username)

        if neworg is None or _user is None:
            return
        parser = Element('body')
        top = SubElement(parser, 'orginfo')
        top.set('orgname', neworg.name)
        top.set('orgnickname', neworg.nickname)
        top.set('type', ConstDef.ORG_ASKJION)
        child = SubElement(top, 'password')
        child.text = neworg.password
        child = SubElement(top, 'creator')
        child.text = neworg.creator
        self._sendpack(_user.address, EnPackType.orginfo.name, tostring(parser, 'utf-8').decode('utf-8'))

    def _recvorginfo(self, dpack: DataPack):
        print('recive orginfo ' + dpack.formatxml())
        parser = XML(dpack.body)
        top = parser.find('orginfo')
        neworg = Org()
        neworg.name = top.get('orgname')
        neworg.nickname = top.get('nickname')
        if top.get('type') == ConstDef.ORG_ASKJION:
            neworg.password = top.get('password')
            neworg.creator = top.get('creator')
            print('do you want join ' + neworg.name + ',yes of course')
            OrgMng.instance().addorg(neworg)
            _user = User()
            _user.parse_data(dpack)
            OrgMng.instance().add_user(neworg.name, _user)
            self.sendlineinfo(IpAddress(Sys_Para.NET_GROUPADDR, Sys_Para.NET_GROUPRPORT), True, False)


