# -*- coding:utf-8 -*-
__author__ = 'tang'
from . import psocket
from . import mthread
from time import sleep
from log import *
from base import *
from socket import INADDR_NONE

class udprecvthd(mthread.mthread,psocket.udpsocket):
#必须用mthread.mthread,如果用mthread会引起歧义导致错误
    def __init__(self,procdata,ip,port,buffsize,group):
        self.group = True
        if group == INADDR_NONE:
            self.__name =  'udprecvthd:' + str(port)
            self.group = False
        else:
            self.__name = 'grouprecvthd:' + str(port)
        mthread.mthread.__init__(self,self.recvdata,sys_para.NET_BUFSIZE)
        psocket.udpsocket.__init__(self)
        self._procthd = procdata
        self.set(ip,
                 port,
                 buffsize,
                 group)
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
            sleep(0.01)
            if data != None:
                print('thd%s  IP:%s port:%d  %s'%(self.__name,ip[0],ip[1],data))
                self._processfunc(net_data(ip[0],ip[1],data,True))

def main():
    udp = udprecvthd()
    udp.set('192.170.41.210',24568,1000)
    udp.start()
    sleep(10)
    udp.stop()
if '__main__' == __name__:
    main()