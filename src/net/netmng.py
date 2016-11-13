# -*- coding:utf-8 -*-
__author__ = 'sun'
from . import dataproc,udprecvthd,udpsendthd
from base import net_data,datapack,sys_para
from time import sleep
from user import user,usermng
class netmng():
    def create(self):
        self._dataproc = dataproc.dataproc()
        self._dataproc.start()

        self._sendthd = udpsendthd.udpsendthd()
        self._sendthd.start()
        sleep(1)
        self._recvthd = udprecvthd.udprecvthd(self._dataproc)
        self._dataproc.setthread(recv = self._recvthd,send = self._sendthd)
        self._recvthd.start()





        dpack = datapack()
        xdoc = ''' <datapack>
        <data_body username= "tang" nickname = "tom" type ="connectstatus">on</data_body>
        </datapack>'''

        dpack.parsexml(xdoc)

        data = net_data(sys_para.NET_GROUPADDR,sys_para.NET_DESTPORT,dpack.formatxml().encode('utf-8'),False)

        for i in range(2):
            self._sendthd.write(data)
            sleep(0.02)

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
</plans>
        </data_body>
        </datapack>'''
        dpack.parsexml(xdoc)
        data = net_data(sys_para.NET_GROUPADDR,sys_para.NET_DESTPORT,dpack.formatxml().encode('utf-8'),False)
        self._sendthd.write(data)
        print('send over')
    def sendofflineinfo(self):
        dpack = datapack(username = usermng.instance().getadmin().name,
                         nickname = usermng.instance().getadmin().nickname,
                         type = en_dp_type.connectstatus.name,constdef.OFFLINE)
        data = net_data(sys_para.NET_GROUPADDR,sys_para.NET_DESTPORT,dpack.formatxml().decode('utf-8'),False)
        if self._sendthd is not None:
            self._sendthd.write(data)
    def exit(self):
        self.sendofflineinfo()
        self._sendthd.stop()
        self._recvthd.stop()
        self._dataproc.stop()




def main():
    netapp = netmng()
    netapp.create()
    sleep(3)
    netapp.exit()
main()
