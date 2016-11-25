# -*- coding:utf-8 -*-
__author__ = 'tang'
from . import psocket
from . import mthread
from time import sleep
from log import *
from base import *
from socket import INADDR_NONE


class UdpRecvThd(mthread.MThread, psocket.UdpSocket):  # 必须用mthread.mthread,如果用mthread会引起歧义导致错误
    def __init__(self, procdata, ip, port, buffsize, group):
        self.group = True
        if group == INADDR_NONE:
            self.__name = 'udprecvthd:' + str(port)
            self.group = False
        else:
            self.__name = 'grouprecvthd:' + str(port)
        mthread.MThread.__init__(self,self.recvdata, Sys_Para.NET_BUFSIZE)
        psocket.UdpSocket.__init__(self)
        self._procthd = procdata
        self.set(ip, port, buffsize, group)
        linfo(self.__name, 'create thread')

    def recvdata(self, data):
        self._procthd.write(data)

    def stop(self):
        super(UdpRecvThd, self).stop()#调用父类方法
        sleep(1.5)  # wait for self.recv() finish,or when recv and close socket,it raise exception
        self.close()
        linfo(self.__name, '线程关闭')
    def read(self):
        while self._brun:
            data, address = self.recv()
            sleep(0.01)
            if data is not None:
                print('thd%s  IP:%s port:%d  %s'%(self.__name, address[0], address[1], data))
                self._processfunc(NetData(address[0], address[1], data, True))

def main():
    udp = UdpRecvThd()
    udp.set('192.170.41.210', 24568, 1000)
    udp.start()
    sleep(10)
    udp.stop()
if '__main__' == __name__:
    main()