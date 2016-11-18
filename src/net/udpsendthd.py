# -*- coding:utf-8 -*-
__author__ = 'tang'
from . import psocket
from . import mthread
from time import sleep
from  base import *
from log import *

class udpsendthd(mthread.mthread,psocket.udpsocket):
#必须用mthread.mthread,如果用mthread会引起歧义导致错误
    def __init__(self):
        self.__name =  'udpsendthread'
        mthread.mthread.__init__(self,self.__senddata,sys_para.NET_BUFSIZE)
        psocket.udpsocket.__init__(self)
        self.set(psocket.getlocalip(),
                 sys_para.NET_LOCALPORT,
                 sys_para.NET_BUFSIZE,
                 sys_para.NET_GROUPADDR)
        linfo(self.__name,'create thread ')
    def __senddata(self,data):
        self.send(data.ip,data.port,data.data)
    def stop(self):
       super(udpsendthd,self).stop()#调用父类方法
       self.close()


def main():
    udp = udpsendthd()
#    udp.set('192.170.41.210',12345,1000,'225.0.0.1')
#    data = ttc_data("225.0.0.2",24568,b'1223344')
    udp.set('192.170.41.210',12345,1000)
    data = net_data("192.170.41.210",24568,b'1223344')
    udp.start()
    udp.write(data)
    for i in range(10):
        udp.write(data)
        sleep(1)
    udp.stop()
#    udp.send("225.0.0.2",24568,b'1223344')
#main()

