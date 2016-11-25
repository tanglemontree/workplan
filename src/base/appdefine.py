from __future__ import absolute_import
# -*- coding:utf-8 -*-
__author__ = 'tang'
from xml.etree import ElementTree
from xml.etree.ElementTree import (XML, Element,
                                               SubElement, tostring)
from enum import Enum
from xml.dom import minidom
from log import mylog, MLog, setlog


class ConstDef():
    VERSION = '0.1'
    ONLINE = 'ON'
    OFFLINE = 'OFFLINE'
    ORG_ASKJION = 'askjoin'
    ORG_RENAME = 'rename'
    ORG_REMOVE = 'remove'


class EnPackType(Enum):
    connectstatus = 1
    workplan = 2
    orginfo = 3


class Sys_Para():
    NET_LOCALPORT = 12321  #发送socket绑定端口号
    NET_UDPRPORT = 18687   #UDP 接收端口号
    NET_GROUPRPORT = 18686  #组播收端口
    NET_GROUPADDR = '231.22.33.44'
    NET_BUFSIZE = 20000


class IpAddress():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port


def prettystr(element, iencoding=None):
    rough_string = ElementTree.tostring(element,'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(encoding=iencoding, indent="   ", newl='\r\n')


class NetData:
    def __init__(self, ip, port, data, brecv=True):
        self.ip = ip
        self.port = port
        self.data = data
        self.brecv = brecv
"""
datapack: application data pack transfer on net
"""


class DataPack:
    def __init__(self, username='', nickname='', type=None, body=''):
        self.username = username
        self.nickname = nickname
        self.ip = ''
        self.type = type
        self.body = body
        self.tag_body = 'data_body'
        self.tag_username = 'username'
        self.tag_type = 'type'
        self.tag_nickname = 'nickname'
        self.__modulename = 'datapack'

    def parsenetdata(self, dnet_data):
        self.ip = dnet_data.ip
        self.parsexml(dnet_data.data.decode('utf-8'))

    def parsexml(self, xdoc):
        self.body = ''
        try:
            parser = XML(xdoc)
            element = parser.find(self.tag_body)
            if element is None:
                return False
            else:
                self.username = element.attrib.get(self.tag_username)
                self.type = element.attrib.get(self.tag_type)
                self.nickname = element.attrib.get(self.tag_nickname)
                self.body = tostring(element, 'utf-8').decode('utf-8')

                # c = list(element)
                # if len(c) == 0:
                #     self.body = element.text
                # else:
                #     for sub in c:
                #         self.body = self.body + tostring(sub,'utf-8').decode('utf-8')
                #         #TODO
                return True
        except Exception as e:
            print('%s:%s' % (self.__modulename, e))

    def formatxml(self):
        top = Element('datapack')
        child = SubElement(top,self.tag_body,
                           {self.tag_username: self.username,
                            self.tag_nickname: self.nickname,
                            self.tag_type: self.type})
        # 上下两种方法都可以设置节点属性
        """
        child = SubElement(top,self.tag_body)
        child.set(self.tag_username,self.username)
        child.set(self.tag_type,self.type)
        """

        bodyelement = XML(self.body)
        if len(bodyelement.getchildren()) > 0:
            for i in bodyelement.getchildren():
                child.append(i)
        return tostring(top, 'utf-8').decode('utf-8')


def main():

    dpack = DataPack()
    xdoc = ''' <datapack>
    <data_body username= "tang" nickname = "tom" type ="connectstatus">on</data_body>
    </datapack>'''

    dpack.parsexml(xdoc)
    dpack.formatxml()
if __name__ == '__main__':
    print('main')
    main()
