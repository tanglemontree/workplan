# -*- coding:utf-8 -*-
__author__ = 'tang'
import datetime
from xml.etree.ElementTree import (XML,Element,ElementTree,parse,
                                               Comment,SubElement,tostring)
from xml.dom.minidom import parseString
import re
from log import linfo,lerror
from base import prettystr,mpath
import uuid
import copy
import os
from functools import cmp_to_key
PLAN_ADD = 'add'
PLAN_REMOVE = 'remove'
PLAN_EDIT = 'edit'
PLAN_DONE = 'done'
PLAN_REPORT = 'report'
PLAN_REPLY = 'reply'
__curplanlist_instance__ = None
__backplanlist_onstance__ = None

class planlist():
    def __init__(self,planname):
        self._planlist = []
        self._planname = planname
        self.readfromfile()
    def list(self):
        return self._planlist
    def querybyid(self,plan):
        index = self._index(plan)
        return self._planlist[index] if index > -1 else None
    def add(self,pl):
        plan = copy.deepcopy(pl)
        if True in [plan.id == p.id for p in self._planlist]:
            return self.edit(plan)
        else:
            self._planlist.append(plan)
            cp = lambda x,y: (x.start - y.start).days
            self._planlist.sort(key = cmp_to_key(cp))
            return True
    def _index(self,pl):
        plan = copy.deepcopy(pl)
        tmp = [plan.id == p.id for p in self._planlist]
        if tmp.count(True) > 0:
            index = [plan.id == p.id for p in self._planlist].index(True)
        else:
            index = -1
        return index
    def edit(self,pl):
        plan = copy.deepcopy(pl)
        index = self._index(plan)
        if  index>= 0:
            self._planlist[index] = plan
            return True
        else:
            return False
    def remove(self,id):
        p = plan()
        p.id = id
        index = self._index(p)
        if index >= 0:
            self._planlist.pop(index)
    def done(self,plan):
        pl = copy.deepcopy(plan)
        pl.progess = 100
        self.remove(pl.id)
        return pl
        #TODO
    def writetofile(self):
        filepath = mpath.inistance().getdatapath() + self._planname
        if len(self._planlist) == 0:
            return
        top = Element('plans')
        for p in self._planlist:
            top.append(XML(p.formatxml()))

        with open(filepath,mode = 'wb') as f:
            f.write(prettystr(top,'utf-8'))
            f.close()

    def readfromfile(self):
        filepath = mpath.inistance().getdatapath() + self._planname
        if os.path.exists(filepath) == False:
            return
        try:
            parser = parse(filepath).getroot()
            if parser == None:
                return
            else:
                 self._planlist = []
                 for p in parser.getchildren():
                     pl = plan()
                     pl.parsexml(p)
                     self.add(pl)
        except Exception as e:
            lerror('',repr(e))


class curplans(planlist):
    def __init__(self):
        global __curplanlist_instance__
        if __curplanlist_instance__ != None:
            return
        planlist.__init__(self,'curplan.xml')
    @staticmethod
    def instance():
        global  __curplanlist_instance__
        if __curplanlist_instance__ == None:
            __curplanlist_instance__ = curplans()
            __curplanlist_instance__.readfromfile()
        return __curplanlist_instance__
    def processbytype(self,pl):
        plan = copy.deepcopy(pl)
        if plan.type == PLAN_ADD:
            print('add plan')
            self.add(plan)
        elif plan.type == PLAN_DONE:
            pl = self.done(plan)
            backplans.instance().add(pl)
            backplans.instance().writetofile()
        elif plan.type == PLAN_EDIT:
            print('edit plan')
            self.edit(plan)
        elif plan.type == PLAN_REMOVE:
            self.remove(plan.id)

class backplans(planlist):
    def __init__(self):
        global __backplanlist_onstance__
        if __backplanlist_onstance__ != None:
            return
        planlist.__init__(self,'history_plan.xml')
    @staticmethod
    def instance():
        global __backplanlist_onstance__
        if __backplanlist_onstance__ == None:
            __backplanlist_onstance__ = backplans()
            __backplanlist_onstance__.readfromfile()
        return __backplanlist_onstance__

class totalplans():
    @staticmethod
    def queryplans(start,end):
        plans = []
        cp = lambda x,y: (x.start - y.start).days
        def query(src,start,end):
            dest = []
            for p in src:
                if (p.start - end).days > 0 or (start - p.end).days > 0:
                    pass
                else:
                    dest.append(p)
            return dest
        plans = query(curplans.instance().list(),start,end) + query(backplans.instance().list(),start,end)
        plans.sort(key = cmp_to_key(cp))
        return plans





class plan():
    def __init__(self):
        self.producer = ''
        self.id = ''
        self.type = None
        self.name = ''
        self.description = ''
        self.start = None
        self.end = None
        self.boss = ''
        self.teammates = []
        self.progress = 0
        self.report = []
        self.orgname = ''
        self._tagorgname = 'orgname'
        self._tagproducer = 'producer'
        self._tagid = 'id'
        self._tagtype = 'type'
        self._tagname = 'name'
        self._tagdescription = 'description'
        self._tagstart = 'start'
        self._tagend = 'end'
        self._tagboss = 'boss'
        self._tagteammate = 'teammate'
        self._tagprogress = 'progress'
        self._tagreport = 'report'

    def setid(self):#只有在生成计划时才需要调用，后续该计划的操作不能再调用该函数，id是计划唯一标识
        self.id = str(uuid.uuid1())
    def tostring(self):
        mates = ''
        for i in self.teammates:
            mates = mates + i + ','
        return 'producer:' + self.producer + '  id=' + self.id + '  起止时间:' + self.start.strftime('%y-%m-%d') + \
            '  ' + self.end.strftime('%y-%m-%d') + '\r\n        名字:' + self.name + '  内容:'+self.description + \
            '  boss:' + self.boss + ' mates:' + mates + ' progess:' + str(self.progress)
    def isboss(self,name):
        if self.boss == name.strip():
            return True
        else:
            return False
    def isproducer(self,name):
        if self.producer == name.strip():
            return True
        else:
            return False
    def addreport(self,plan):
        self.progress = plan.progress
        self.report = self.report + plan.report
    def isteammate(self,name):
        if self.teammates.count(name.strip()) > 1:
            return True
        else:
            return False
    def formatxml(self):
        try:
            top = Element('plan')
            SubElement(top,self._tagorgname).text = self.orgname
            SubElement(top,self._tagproducer).text = self.producer
            SubElement(top,self._tagid).text = str(self.id)
            SubElement(top,self._tagtype).text = self.type
            SubElement(top,self._tagname).text = self.name
            SubElement(top,self._tagdescription).text = self.description
            SubElement(top,self._tagstart).text = self.start.strftime('%y-%m-%d')
            SubElement(top,self._tagend).text = self.end.strftime('%y-%m-%d')
            SubElement(top,self._tagboss).text = self.boss

            for mate in self.teammates:
                SubElement(top,self._tagteammate).text = mate
            SubElement(top,self._tagprogress).text = str(self.progress)
            if self.type == PLAN_REPORT:
                for report in self.report:
                    SubElement(top,self._tagreport).text = report
            return tostring(top,'utf-8').decode('utf-8')
        except Exception as e:
            lerror('',str(e))
            return ''

    def parsexml(self, parser):
        try:
            self.id = parser.find(self._tagid).text.strip()
            self.type = parser.find(self._tagtype).text.strip().lower()
            if parser.find(self._tagorgname) is not None:
                self.orgname = parser.find(self._tagorgname).text.strip()
            if self.type == PLAN_REPORT:
                self.report.append(datetime.now().date().strftime('%y-%m-%d:') + parser.find(self._tagreport).text.strip())
                self.progress = int(parser.find(self._tagprogress).text.strip())
                if self.progress > 100:
                    self.progress = 100
                elif self.progress < 0:
                    self.progress = 0
                return True
            elif self.type == PLAN_REPLY:
                return True

            self.producer = parser.find(self._tagproducer).text.strip()
            self.name = parser.find(self._tagname).text.strip()
            self.description = parser.find(self._tagdescription).text.strip()
            strdate = str(parser.find(self._tagstart).text.strip())
            for strdate in [parser.find(self._tagstart).text.strip(),parser.find(self._tagend).text.strip()]:
                if re.match('\d\d-[0-1]?[0-9]-[0-1]?[0-9]',strdate) is None:
                    lerror('',('plan date format is wrong(%s),right format is yy-mm-dd. ' % strdate))
                    return False
            self.start = datetime.datetime.strptime(parser.find(self._tagstart).text.strip(),"%y-%m-%d")
            #strptime只接受年为两位，0-68就是20XX，69-99就是19XX
            self.end = datetime.datetime.strptime(parser.find(self._tagend).text.strip(),"%y-%m-%d")
            if self.start > self.end:
                lerror('','开始时间晚于结束时间')
                return False
            self.boss = parser.find(self._tagboss).text.strip()
            element = parser.findall(self._tagteammate)
            self.teammates = []
            for child in element:
                self.teammates.append(child.text.strip())
            return True
        except Exception as e:
            lerror('',str(e))
            return False

def test():
    p = plan()

    xdoc = '''
<plan>
<producer>manager</producer>
<id>342343</id>
<type>add</type>
<name>需求阶段</name>
<description>软件需求文档</description>
<start>16-09-12</start>
<end>16-09-16</end>
<boss>gates</boss>
<teammate>bob</teammate>
<teammate>lucy</teammate>
<progress>90</progress >
</plan>
'''
    parser = XML(xdoc)
    p.parsexml(parser)
    print(p.formatxml())
    ps = planlist()
    ps.add(p)

    ps.writetofile()
#test()


