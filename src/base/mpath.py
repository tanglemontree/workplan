__author__ = 'Administrator'
import os,io

__instance_mpath__ = None
__havempath_instance__ = False
class mpath():
    def __init__(self):
        global __instance_mpath__,__havempath_instance__
        if __instance_mpath__ != None:
            return
        cwd = os.getcwd()
        cc = cwd.split(os.sep)
        self._root = cwd.rstrip(cc[-1])
        self._log = self._root  + 'log'+ os.sep
        if not os.path.exists(self._log):
            os.makedirs(self._log)
        self._data = self._root+ 'data' + os.sep
        if not os.path.exists(self._data):
            os.makedirs(self._data)
        self._config = self._root + 'config' + os.sep
        if not os.path.exists(self._config):
            os.makedirs(self._config)
        __havempath_instance__ = True
    @staticmethod
    def inistance():
        global __instance_mpath__
        if __instance_mpath__ == None:
            __instance_mpath__ = mpath()
        return __instance_mpath__
    def getroot(self):
        return self._root
    def getlogpath(self):
        return self._log
    def getconfigpath(self):
        return self._config
    def getdatapath(self):
        return self._data

def test():
    p = mpath()
    p.getroot()

test()
