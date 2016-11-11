# -*- coding:utf-8 -*-
__author__ = 'tang'
"""
<plans>
<plan>
<producer>manager</producer>
<id>342343</id>
<type>add</type>
<name>需求阶段</name>
<description>软件需求文档</description>
<start>2016-9-12</start>
<end>2016-9-16</end>
<boss>gates</boss>
<teammate>bob</teammate>
<teammate>lucy</teammate>
<progress>90</progress >
</plan>
</plans>
"""

import datetime
from xml.etree.ElementTree import (XML,Element,
                                               Comment,SubElement,tostring)
import re
from log import linfo,lerror
from base import prettystr
PLAN_ADD = 'add'
PLAN_REMOVE = 'remove'
PLAN_EDIT = 'edit'
PLAN_DONE = 'done'
class planlist():
    def __init__(self):
        self._planlist = []
    def add(self,plan):
        if True in [plan.id == p.id for p in self._planlist]:
            return self.edit(plan)
        else:
            self._planlist.append(plan)
            return True
    def _index(self,plan):
        tmp = [plan.id == p.id for p in self._planlist]
        if tmp.count(True) > 0:
            index = [plan.id == p.id for p in self._planlist].index(True)
        else:
            index = -1
        return index
    def edit(self,plan):
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
        plan()
        #TODO
    def writetofile(self,filepath):

        top = Element('plans')
        for p in self._planlist:
            top.append(XML(p.formatxml()))
        print('have plans',len(list(top)))
        with open(filepath,mode = 'wb') as f:
            f.write(prettystr(top,'utf-8'))

    def processbytype(self,plan):
        if plan.type == PLAN_ADD:
            print('add plan')
            self.add(plan)
        elif plan.type == PLAN_DONE:
            self.done(plan)
        elif plan.type == PLAN_EDIT:
            print('edit plan')
            self.edit(plan)
        elif plan.type == PLAN_REMOVE:
            self.remove(plan.id)
        self.writetofile('c:\plans.xml')



class plan():
    def __init__(self):
        self.producer = ''
        self.id = 0
        self.type = None
        self.name = ''
        self.description = ''
        self.start = None
        self.end = None
        self.boss = ''
        self.teammates = []
        self.progress = 0
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
    def isboss(self,name):
        if self.boss == name.strip():
            return True
        else:
            return False
    def isteammate(self,name):
        if self.teammates.count(name.strip()) > 1:
            return True
        else:
            return False
    def formatxml(self):
        try:
            top = Element('plan')
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

            return tostring(top,'utf-8').decode('utf-8')
        except Exception as e:
            lerror('',str(e))
            return ''

    def parsexml(self, parser):
        try:
            self.producer = parser.find(self._tagproducer).text.strip()
            self.id = int(parser.find(self._tagid).text.strip())
            self.type = parser.find(self._tagtype).text.strip().lower()
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
            for child in element:
                self.teammates.append(child.text.strip())
            self.progress = int(parser.find(self._tagprogress).text.strip())
            if self.progress > 100:
                self.progress = 100
            elif self.progress < 0:
                self.progress = 0
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

    ps.writetofile(r'c:\plans.xml')
#test()


