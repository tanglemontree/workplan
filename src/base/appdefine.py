from __future__ import absolute_import
# -*- coding:utf-8 -*-
__author__ = 'tang'
import os,sys
from xml.etree import ElementTree
from xml.etree.ElementTree import (XML,Element,
                                               Comment,SubElement,tostring)
from enum import Enum
from xml.dom import minidom
from log import mylog,mlog,setlog

class constdef():
    ONLINE = 'ON'
    OFFLINE = 'OFFLINE'
class en_dp_type(Enum):
    connectstatus = 1
    workplan = 2

class sys_para():
    NET_LOCALPORT = 12321
    NET_DESTPORT = 18686
    NET_GROUPADDR = '231.22.33.44'
    NET_BUFSIZE = 20000

def prettystr(element,iencoding = None):

    rough_string = ElementTree.tostring(element,'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(encoding= iencoding,indent="   ")
class net_data:
    def __init__(self,ip,port,data,brecv = True):
        self.ip = ip
        self.port = port
        self.data = data
        self.brecv = brecv
"""
datapack: application data pack transfer on net
"""
class datapack:
    def __init__(self,username='',nickname = '',type=None,body=''):
        self.username = username
        self.nickname = nickname
        self.type = type
        self.body = body
        self.tag_body = 'data_body'
        self.tag_username = 'username'
        self.tag_type = 'type'
        self.tag_nickname = 'nickname'
        self.__modulename = 'datapack'
    def parsenetdata(self,dnet_data):
        self.ip = dnet_data.ip
        self.parsexml(dnet_data.data.decode('utf-8'))
    def parsexml(self,xdoc):
        self.body = ''
        try:
            parser = XML(xdoc)
            element = parser.find(self.tag_body)
            if  element ==  None:
                return False
            else:
                self.username = element.attrib.get(self.tag_username)
                self.type = element.attrib.get(self.tag_type)
                c = list(element)
                if len(c) == 0:
                    self.body = element.text
                else:
                    for sub in c:
                        self.body = self.body + tostring(sub,'utf-8').decode('utf-8')
                        #TODO

                self.nickname = element.attrib.get(self.tag_nickname)
                return True
        except Exception as e:
            print('%s:%s'%(self.__modulename,e))
    def parsedata(self):
        if self.type == en_dp_type.connectstatus.name:
            return self.type,self.body
    def formatxml(self):
        top = Element('datapack')
        child = SubElement(top,self.tag_body,{
            self.tag_username:self.username,
            self.tag_nickname:self.nickname,
            self.tag_type:self.type})
        #上下两种方法都可以设置节点属性
        """
        child = SubElement(top,self.tag_body)
        child.set(self.tag_username,self.username)
        child.set(self.tag_type,self.type)
        """
        xdoc = '<body>'+self.body+'</body>'
        bodyelement = XML(xdoc)
        if len(bodyelement.getchildren()) > 0:
            for i in bodyelement.getchildren():
                child.append(i)
        else:
            child.text = self.body


        str = tostring(top,'utf-8').decode('utf-8')
       # print(str)

        return str
def test():
    mylog.__loglevel__ = mylog.ERROR
    setlog('gggglog.txt',mylog.ERROR)
    mlog.instance().warn('main','dddxxxxx')
    mlog.instance().error('main','EEEExxxxx')
    with open(mlog.instance().getpath(),'rt') as f:
        logtext = f.read()
#    print(logtext)

def main():

    dpack = datapack()
    xdoc = ''' <datapack>
    <data_body username= "tang" nickname = "tom" type ="connectstatus">on</data_body>
    </datapack>'''

    dpack.parsexml(xdoc)
    dpack.formatxml()
    test()
if  __name__== '__main__':
    print('main')
    main()
