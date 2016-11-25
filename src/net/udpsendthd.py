# -*- coding:utf-8 -*-
__author__ = 'tang'
from . import psocket
from . import mthread
from time import sleep
from  base import *
from log import *


class UdpSendThd(mthread.MThread, psocket.UdpSocket):  # 必须用mthread.mthread,如果用mthread会引起歧义导致错误
    def __init__(self):
        self.__name = 'udpsendthread'
        mthread.MThread.__init__(self, self.__senddata, Sys_Para.NET_BUFSIZE)
        psocket.UdpSocket.__init__(self)
        self.set(psocket.getlocalip(), Sys_Para.NET_LOCALPORT, Sys_Para.NET_BUFSIZE, Sys_Para.NET_GROUPADDR)
        linfo(self.__name, 'create thread ')

    def __senddata(self, data):
        self.send(data.ip, data.port, data.data)

    def stop(self):
        super(UdpSendThd, self).stop()  # 调用父类方法
        self.close()
        linfo(self.__name, '关闭线程')


def main():
    udp = UdpSendThd()
#    udp.set('192.170.41.210',12345,1000,'225.0.0.1')
#    data = ttc_data("225.0.0.2",24568,b'1223344')
    udp.set('192.170.41.210', 12345, 1000)
    data = NetData("192.170.41.210", 24568, b'1223344')
    udp.start()
    udp.write(data)
    for i in range(10):
        udp.write(data)
        sleep(1)
    udp.stop()
#    udp.send("225.0.0.2",24568,b'1223344')
#main()

