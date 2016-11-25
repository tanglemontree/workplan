# -*- coding:utf-8 -*-
__author__ = 'tang'
import threading
from queue import Queue
from time import sleep


class MThread(threading.Thread):
    def __init__(self, func, maxqueuesize):
        threading.Thread.__init__(self)
        self.__name = 'mthread'
        self.__maxqueuesize = 1000 if maxqueuesize < 1000 else maxqueuesize
        self.__revqueue = Queue(self.__maxqueuesize)
        self.__secqueue = Queue(self.__maxqueuesize)
        self._processfunc = func
        self._brun = True

    def run(self):
        self.read()

    def stop(self):
        self._brun = False

    def read(self):
        while self._brun:
            while self.__revqueue.qsize() > 0:
                self.__secqueue.put(self.__revqueue.get(1))
            if self.__secqueue.empty():
                sleep(0.05)
                continue
            while self.__secqueue.qsize() > 0:
                self._processfunc(self.__secqueue.get(1))
                # print(' read qsize')
    #    print('end read')

    def write(self, data):
        self.__revqueue.put(data)

def main():
    t = MThread(3000)
    t.start()
    t.write(1)
    sleep(1)
    t.stop()

#main()
