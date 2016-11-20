__author__ = 'twt'
from log import *
from net import netmng,getlocalip
from user import user,usermng,org,orgmng
from base import mpath,datapack,net_data,sys_para,ipaddress
from socket import gethostname
from plan import plan,backplans,curplans,totalplans,PLAN_REMOVE
from xml.etree.cElementTree import XML,Element
from datetime import datetime
class mainproc:
    def __init__(self):

        self._modulename = '主程序'
        setlog(mpath.inistance().getlogpath()+str(datetime.now().date()) + "log.txt",DEBUG)
        self._netmng = None
        if None == usermng.instance().getadmin():
            u = self.create_account()
            if u == None:
                lwarn(self._modulename,"未建立账户，程序退出")
                return
            else:
                u.addr = ipaddress(getlocalip(),sys_para.NET_UDPRPORT)
        else:
            u = usermng.instance().getadmin()
            u.addr = ipaddress(getlocalip(),sys_para.NET_UDPRPORT)

        usermng.instance().setadmin(u)
        usermng.instance().writetofile()
        print('welcome '+usermng.instance().getadmin().nickname + '!')
        self._netmng = netmng.netmng()

        dpack = datapack()
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
            p = plan()
            p.parsexml(c)
            curplans.instance().add(p)
        curplans.instance().writetofile()


    def create_account(self):
        u = user()
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
        return u
    def exit(self):
        if self._netmng:
            self._netmng.exit()
        usermng.instance().writetofile()
        curplans.instance().writetofile()
        backplans.instance().writetofile()
    def oncmd(self,cmd):
        cmd = cmd.strip()
        if cmd == 'online':
            self._netmng.sendlineinfo(ipaddress(sys_para.NET_GROUPADDR,sys_para.NET_GROUPRPORT),True,False)
        elif cmd == 'offline':
            self._netmng.sendlineinfo(ipaddress(sys_para.NET_GROUPADDR,sys_para.NET_GROUPRPORT),False,False)
        elif cmd[0:8] == 'add plan':#add plan [plan_xml]
            self.addplan(cmd[8:])
        elif cmd[0:11] == 'remove plan':
            self.removeplan(cmd[11:])
        elif cmd[0:9] == 'edit plan':
            self.editplan(cmd[9:])
        elif cmd[0:9] == 'send plan':#'send plan [index]:
            self.sendplan(cmd[10:])
        elif cmd == 'userlist':
            self.showuserlist()
        elif cmd == 'planlist':
            self.showcurplan()
        elif cmd[0:10] == 'query plan':
            tmp = cmd[11:].split(' ')
            if len(tmp) != 2:
                print('input wrong cmd.(query plan yy-mm-dd yy-mm-dd')
                return
            self.queryplan(tmp[0],tmp[1])
        elif cmd[0:8] == 'add user':
            self.adduser(cmd[8:])

        elif cmd[0:10] == 'addorguser':
            cmds = cmd[11:].split(' ')
            if len(cmds) != 2:
                print('wrong cmd(addorguser orgname username')
                return
            self.addorguser(cmds[0],cmds[1])
        elif cmd[0:7] == 'orginfo':
            self.showorginfo()
        elif cmd[0:10] == 'create org':
            cmds = cmd[11:].split(' ')
            if len(cmds) == 3:
                self.createorg(cmds[0],cmds[1],cmds[2])
            else:
                print('cmd format is wrong.(create org orgname nickname password')

        else:
            print('unkown cmd!')
            return

    def adduser(self,cmd):
        cmd = cmd.strip()
        cmds = cmd.split(' ')
        if len(cmds) < 5:
            print('cmd error (add user name nickname ip port email')
        u = user(name =cmds[0],nickname= cmds[1],addr = ipaddress(cmds[2],int(cmds[3])),online=True)
        u.email = cmds[4]
        usermng.instance().add(u)
        usermng.instance().writetofile()
    def showuserlist(self):
         [print(i.nickname+'(' + i.name+'):' + "  IP:"+ i.addr.ip + ('  online' if i.online else '  offline')   )for i in usermng.instance().list()]
    def showcurplan(self):
        self._showplan(curplans.instance().list())
    def showorginfo(self):
        for orgname in orgmng.instance().map().keys():
            users = ''
            for u in orgmng.instance().getuserlist(orgname).list():
                users += u.name + "  "
            print('[org] ' + orgname + " :"+users)
    def sendplan(self,index):
#        index = '0,2'
        if index.count(' ') == 0:
            n = int(index)
            if int(n) < len(curplans.instance().list()):
                self._netmng.sendplans([curplans.instance().list()[int(index)]])
        else:
            nindex = index.split(' ')
            plans = []
            for n in nindex:
                if int(n) < len(curplans.instance().list()):
                    plans.append(curplans.instance().list()[int(n)])
            self._netmng.sendplans(plans)
    def _showplan(self,plans):
        index = 0
        if plans == None:
            return
        for p in plans:
            print("  "+str(index)+':'+p.tostring())
            index += 1
    def addplan(self,xdoc):

        pl = plan()
        parser = None
        try:
            parser = XML(xdoc)
        except Exception as e:
            print(e)
            return
        if parser == None:
            print('plan(xml) is 错误格式！')
            return
        for e in parser.getchildren():
            pl.parsexml(e)
            pl.setid()
            curplans.instance().add(pl)
        curplans.instance().writetofile()
    def removeplan(self,cmd):
        index = int(cmd.strip())
        if index < len(curplans.instance().list()):
            _plan = curplans.instance().list()[index]
            _plan.type = PLAN_REMOVE
            curplans.instance().remove(_plan.id)
            backplans.instance().add(_plan)
            self._netmng.sendplans([_plan])
    def editplan(self,cmd):#test
        index = int(cmd.strip())
        if index < len(curplans.instance().list()):
            _plan = curplans.instance().list()[index]
            _plan.description = 'edit plan'
            self._netmng.sendplans([_plan])
    def createorg(self,orgname,nickname,password):
        creator = usermng.instance().getadmin().name
        neworg = org(orgname,nickname,password,creator)
        orgmng.instance().addorg(neworg)
    def addorguser(self,orgname,username):
        self._netmng.addorguser(orgname,username)
    def queryplan(self,start,end):
    #    start = '2015-12-3'
    #    end = '16-12-1'
        def str2date(sdate):
            dates = sdate.split('-')

            if len(dates) != 3:
                return None
            if len(dates[0]) == 4:
                dates[0] = dates[0][2:]
            return datetime.strptime('{0}-{1}-{2}'.format(dates[0],dates[1],dates[2]),'%y-%m-%d')
        dstart = str2date(start)
        dend = str2date(end)
        if dstart != None and dend != None:
            plans = totalplans.queryplans(dstart,dend)
            self._showplan(plans)












def main():
    proc = mainproc()
    cmd = input('please input cmd: ')
    while cmd.strip() != 'exit':
        proc.oncmd(cmd)
        cmd = input('please input cmd: ')

    proc.exit()
    #p
main()