# -*- coding:utf-8 -*-
__author__ = 'twt'
from . import dataprocess, udprecvthd, udpsendthd
from base import DataPack, Sys_Para, IpAddress
from time import sleep
from .psocket import getlocalip
from user import User, UserMng
from socket import INADDR_NONE


class NetMng():
    def __init__(self):
        self.create()

    def create(self):
        self._dataproc = dataprocess.DataProcess()
        self._dataproc.start()

        self._sendthd = udpsendthd.UdpSendThd()
        self._sendthd.start()
        sleep(1)
        self._dataproc.setthread(send=self._sendthd)
        self._recvp2p = udprecvthd.UdpRecvThd(self._dataproc, getlocalip(),
                                              Sys_Para.NET_UDPRPORT,
                                              Sys_Para.NET_BUFSIZE, INADDR_NONE)
        self._recvp2p.start()

        self._recvthd = udprecvthd.UdpRecvThd(self._dataproc, getlocalip(),
                                              Sys_Para.NET_GROUPRPORT,
                                              Sys_Para.NET_BUFSIZE,
                                              Sys_Para.NET_GROUPADDR)
        self._recvthd.start()
        sleep(1)
        self._dataproc.sendlineinfo( IpAddress(Sys_Para.NET_GROUPADDR,
                                               Sys_Para.NET_GROUPRPORT),
                                     True, False)  # 广播上线信息

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
<boss>gates</boss>
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
<teammate>bob</teammate>
<teammate>lucy</teammate>
<progress>90</progress >
</plan>
</plans>        <plans>
        <plan>
<producer>manager</producer>
<id>342343</id>
<type>add</type>
<name>需求阶段</name>
<description>软件需求文档</description>
<start>16-9-12</start>
<end>16-9-16</end>
<boss>gates</boss>
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
<teammate>bob</teammate>
<teammate>lucy</teammate>
<progress>90</progress >
</plan>
</plans>
        </data_body>
        </datapack>'''
        dpack.parsexml(xdoc)
#        data = net_data(sys_para.NET_GROUPADDR,sys_para.NET_GROUPRPORT,dpack.formatxml().encode('utf-8'),False)
#        self._sendthd.write(data)
#        print('send over')

    def sendlineinfo(self, ip, status, isreply):
        self._dataproc.sendlineinfo(ip, status, isreply)

    def sendplans(self, plans):
        self._dataproc.sendplans(plans)

    def addorguser(self, orgname, username):
        self._dataproc.addorguser(orgname, username)

    def exit(self):
        self.sendlineinfo(IpAddress(Sys_Para.NET_GROUPADDR, Sys_Para.NET_GROUPRPORT), False, False)
        sleep(0.4)
        self._sendthd.stop()
        self._recvthd.stop()
        self._recvp2p.stop()
        self._dataproc.stop()


def main():
    netapp = NetMng()
    netapp.create()
    sleep(3)
    netapp.exit()
if __name__ == '__main__':
    main()
