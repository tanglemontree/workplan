# -*- coding:utf-8 -*-
__author__ = 'tang'
from . import psocket
from . import mthread
from time import sleep
from log import *
from base import *
class udprecvthd(mthread.mthread,psocket.udpsocket):
#必须用mthread.mthread,如果用mthread会引起歧义导致错误
    def __init__(self,procdata):
        self.__name =  'udprecvthead'
        mthread.mthread.__init__(self,self.recvdata,sys_para.NET_BUFSIZE)
        psocket.udpsocket.__init__(self)
        self._procthd = procdata
        self.set(psocket.getlocalip(),
                 sys_para.NET_DESTPORT,
                 sys_para.NET_BUFSIZE,
                 sys_para.NET_GROUPADDR)
        linfo(self.__name,'create thread')


    def recvdata(self,data):
        self._procthd.write(data)

    def stop(self):
        super(udprecvthd,self).stop()#调用父类方法
        sleep(1.5)#wait for self.recv() finish,or when recv and close socket,it raise exception
        self.close()
    def read(self):
        while self._brun:
            data,ip = self.recv()
            sleep(1)
            if data != None:
                self._processfunc(net_data(ip[0],1000,data,True))


def main():
    udp = udprecvthd()
    udp.set('192.170.41.210',24568,1000)
    udp.start()
    sleep(10)
    udp.stop()
if '__main__' == __name__:
    main()