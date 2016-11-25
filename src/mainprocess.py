__author__ = 'twt'
from log import *
from net import netmng, getlocalip
from user import User, UserMng, Org, OrgMng, create_account
from base import MPath, DataPack, Sys_Para, IpAddress
from socket import gethostname
from plan import Plan, BackPlans, CurPlans, TotalPlans, PLAN_REMOVE
from xml.etree.cElementTree import XML
from datetime import datetime
from time import sleep

class MainProcess:
    def __init__(self):
        self._modulename = '主程序'
        setlog(MPath.instance().getlogpath()+str(datetime.now().date()) + "log.txt",DEBUG)
        self._netmng = None
        if None == UserMng.instance().getadmin():
            u = create_account()
            if u is None:
                lwarn(self._modulename, "未建立账户，程序退出")
                return
            else:
                u.address = IpAddress(getlocalip(), Sys_Para.NET_UDPRPORT)
        else:
            u = UserMng.instance().getadmin()
            u.address = IpAddress(getlocalip(), Sys_Para.NET_UDPRPORT)

        UserMng.instance().setadmin(u)
        UserMng.instance().writefile()
        print('welcome '+UserMng.instance().getadmin().nickname + '!')
        self._netmng = netmng.NetMng()

        dpack = DataPack()
        xdoc = ''' <datapack>
        <data_body username= "tang" nickname = "tom" type ="workplan">
        <plans>
        <plan>
<producer>manager</producer>
<id>342343</id>
<type>add</type>
<name>需求阶段</name>
<description>软件需求文档</description>
<start>16-9-12</start>
<end>16-9-16</end>
<boss>tang7TEIVUETKULYA2F</boss>
<teammate>bob</teammate>
<teammate>lucy</teammate>
<progress>90</progress >
</plan>
<plan>
<producer>manager</producer>
<id>23343</id>
<type>add</type>
<name>需求阶段</name>
<description>软件需求文档</description>
<start>16-9-18</start>
<end>16-9-26</end>
<boss>gates</boss>
<teammate>tang7TEIVUETKULYA2F</teammate>
<teammate>lucy</teammate>
<progress>90</progress >
</plan>
</plans>
        </data_body>
        </datapack>'''
        dpack.parsexml(xdoc)
        top = XML(dpack.body)
        for c in top.find('plans').getchildren():
            p = Plan()
            p.parsexml(c)
            CurPlans.instance().add(p)
        CurPlans.instance().writefile()

    def exit(self):
        if self._netmng:
            self._netmng.exit()
        UserMng.instance().writefile()
        CurPlans.instance().writefile()
        BackPlans.instance().writefile()

    def oncmd(self, cmd):
        cmd = cmd.strip()
        if cmd == 'online':
            self._netmng.sendlineinfo(IpAddress(Sys_Para.NET_GROUPADDR,Sys_Para.NET_GROUPRPORT),True,False)
        elif cmd == 'offline':
            self._netmng.sendlineinfo(IpAddress(Sys_Para.NET_GROUPADDR,Sys_Para.NET_GROUPRPORT),False,False)
        elif cmd[0:8] == 'add plan':
            self.addplan(cmd[8:])
        elif cmd[0:11] == 'remove plan':
            self.removeplan(cmd[11:])
        elif cmd[0:9] == 'edit plan':
            self.editplan(cmd[9:])
        elif cmd[0:9] == 'send plan':
            self.sendplan(cmd[10:])
        elif cmd == 'userlist':
            self.show_userlist()
        elif cmd == 'planlist':
            self.show_curplan()
        elif cmd[0:10] == 'query plan':
            tmp = cmd[11:].split(' ')
            if len(tmp) != 2:
                print('input wrong cmd.(query plan yy-mm-dd yy-mm-dd')
                return
            self.queryplan(tmp[0], tmp[1])
        elif cmd[0:8] == 'add user':
            self.add_user(cmd[8:])
        elif cmd[0:10] == 'addorguser':
            cmds = cmd[11:].split(' ')
            if len(cmds) != 2:
                print('wrong cmd(addorguser orgname username')
                return
            self.addorguser(cmds[0], cmds[1])
        elif cmd[0:7] == 'orginfo':
            self.showorginfo()
        elif cmd[0:10] == 'create org':
            cmds = cmd[11:].split(' ')
            if len(cmds) == 3:
                self.createorg(cmds[0], cmds[1], cmds[2])
            else:
                print('cmd format is wrong.(create org orgname nickname password')
        else:
            print('unkown cmd!')
            return

    def add_user(self, cmd):
        cmd = cmd.strip()
        cmds = cmd.split(' ')
        if len(cmds) < 5:
            print('cmd error (add user name nickname ip port email')
        u = User(name=cmds[0], nickname=cmds[1], address=IpAddress(cmds[2], int(cmds[3])), online=True)
        u.email = cmds[4]
        # test bellow
        u.qq = '1223444'
        u.wechat = '1377823445'
        u.officephone = '010-82344'
        u.privatephone = '029-22222'
        u.male = False
        u.unit = 'PLC'
        u.officeaddress = 'tiananmen-5'
        UserMng.instance().add(u)
        UserMng.instance().writefile()

    def show_userlist(self):
         [print(i.nickname+'(' + i.name+'):' + "  IP:" + i.address.ip + ('  online' if i.online else '  offline')   )for i in UserMng.instance().list()]
    def show_curplan(self):
        self._showplan(CurPlans.instance().list())
    def showorginfo(self):
        for orgname in OrgMng.instance().map().keys():
            users = ''
            for u in OrgMng.instance().getuserlist(orgname).list():
                users += u.name + "  "
            print('[org] ' + orgname + " :"+users)
    def sendplan(self,index):
#        index = '0,2'
        if index.count(' ') == 0:
            n = int(index)
            if int(n) < len(CurPlans.instance().list()):
                self._netmng.sendplans([CurPlans.instance().list()[int(index)]])
        else:
            nindex = index.split(' ')
            plans = []
            for n in nindex:
                if int(n) < len(CurPlans.instance().list()):
                    plans.append(CurPlans.instance().list()[int(n)])
            self._netmng.sendplans(plans)

    def _showplan(self, plans):
        index = 0
        if plans is None:
            return
        for p in plans:
            print("  "+str(index)+':'+p.tostring())
            index += 1

    def addplan(self, xdoc):
        pl = Plan()
        try:
            parser = XML(xdoc)
        except Exception as e:
            print(e)
            return
        if parser is None:
            print('plan(xml) is 错误格式！')
            return
        for e in parser.getchildren():
            pl.parsexml(e)
            pl.setid()
            CurPlans.instance().add(pl)
        CurPlans.instance().writefile()

    def removeplan(self, cmd):
        index = int(cmd.strip())
        if index < len(CurPlans.instance().list()):
            _plan = CurPlans.instance().list()[index]
            _plan.type = PLAN_REMOVE
            CurPlans.instance().remove(_plan.id)
            BackPlans.instance().add(_plan)
            self._netmng.sendplans([_plan])

    def editplan(self,cmd):
        index = int(cmd.strip())
        if index < len(CurPlans.instance().list()):
            _plan = CurPlans.instance().list()[index]
            _plan.description = 'edit plan'
            self._netmng.sendplans([_plan])

    def createorg(self, orgname, nickname, password):
        creator = UserMng.instance().getadmin().name
        neworg = Org(orgname, nickname, password, creator)
        OrgMng.instance().addorg(neworg)

    def addorguser(self, orgname, username):
        self._netmng.addorguser(orgname, username)

    def queryplan(self, start, end):
    #    start = '2015-12-3'
    #    end = '16-12-1'
        def str2date(sdate):
            dates = sdate.split('-')

            if len(dates) != 3:
                return None
            if len(dates[0]) == 4:
                dates[0] = dates[0][2:]
            return datetime.strptime('{0}-{1}-{2}'.format(dates[0], dates[1], dates[2]), '%y-%m-%d')
        dstart = str2date(start)
        dend = str2date(end)
        if dstart is not None and dend is not None:
            plans = TotalPlans.queryplans(dstart, dend)
            self._showplan(plans)
def checkplans():
    def checktime(plan):
        delttime = plan.end - datetime.now()
        if delttime.days < 0:
            return -1 # 过期
        elif (delttime.days < (plan.end - plan.start).days / 3)\
                or delttime.days < 2:
            return 0 # 快到期
        else:
            return 1 #还在进行中

    for plan in CurPlans.instance().list():
        result = checktime(plan)
        if plan.progress == 100:
            CurPlans.remove(plan.id)
            BackPlans.add(plan)
            CurPlans.writefile()
            BackPlans.writefile()
            continue
        if result == -1:
            lwarn('', plan.name + ':计划已经超期但是仍未完成')
        elif result == 0:
            lwarn('', plan.name + ' :计划快到期，请抓紧时间')
        else:
            pass

def main():
    proc = MainProcess()
    sleep(2)
    cmd = input('please input cmd: ')
    while cmd.strip() != 'exit':
        proc.oncmd(cmd)
        checkplans()
        cmd = input('please input cmd: ')

    proc.exit()
    #p
main()