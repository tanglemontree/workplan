# -*- coding:utf-8 -*-
__author__ = 'tang'
import logging
import sys, os,io,traceback

__loglevel__ = logging.DEBUG
__logpath__ = 'logw.txt'
__instance_mlog__ = None
#__havemlog_instance__ = False
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR



def setlog(path,level):
    global __loglevel__,__logpath__
    __loglevel__ = level
    __logpath__ = path

lwarn = lambda modulename,msg,mode = 'normal' :mlog.instance().warn(modulename,msg,mode)
lerror = lambda modulename,msg,mode = 'normal':mlog.instance().error(modulename,msg,mode)
linfo = lambda modulename,msg,mode = 'normal':mlog.instance().info(modulename,msg,mode)
ldebug = lambda modulename,msg,mode = 'normal':mlog.instance().debug(modulename,msg,mode)
logfunc = ['lwarn(','lerror','linfo(','ldebug']

if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
else: #pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[2].tb_frame.f_back
_srcfile = os.path.normcase(setlog.__code__.co_filename)

class mlog:
    def __init__(self):
        global __instance_mlog__,__logpath__,__loglevel__
        if __instance_mlog__ != None:
            return
        FORMAT = '%(asctime)-15s[%(modulename)s]%(message)s'
        logging.basicConfig(filename = __logpath__,level = __loglevel__,format = FORMAT)
        self._log = logging.getLogger()
        self.path = __logpath__
     #   print('inst')
    def getpath(self):
        return self.path
    def getlog(self):
        return self._log
    @staticmethod
    def instance():
        global __instance_mlog__
        if __instance_mlog__ == None:
            __instance_mlog__ = mlog()
            print('create log')
        return __instance_mlog__
    def processlog(self,modulename,msg,mode = 'normal'):
        #TODO
        print(modulename+" :"+msg)
        return
    def procmanylog(self,modulename,msg):
        #TODO
        return
    def warn(self,modulename,msg,mode = 'normal'):
        sinfo = None
        try:
            fn, lno, func, sinfo = self.findCaller(True)
        except ValueError: # pragma: no cover
            fn, lno, func,sinfo = "(unknown file)", 0, "(unknown function)",""
        if mode == 'many':
            self.procmanylog(modulename,msg)
            return
        else:
            self._log.warning(msg,extra = {'modulename': sinfo})
        print('processlog')
        self.processlog(modulename,msg,mode)
        print('ok')

    def info(self,modulename,msg,mode = 'normal'):
        if mode == 'many':
            self.procmanylog(modulename,msg)
            return
        else:
            self._log.info(msg,extra = {'modulename': modulename})
        self.processlog(modulename,msg,mode)

    def debug(self,modulename,msg,mode = 'normal'):
        if mode == 'many':
            self.procmanylog(modulename,msg)
            return
        else:
            self._log.debug(msg,extra = {'modulename': modulename})
        self.processlog(modulename,msg,mode)

    def error(self,modulename,msg,mode = 'normal'):
        try:
            fn, lno, func, sinfo = self.findCaller(True)
        except ValueError: # pragma: no cover
            fn, lno, func,sinfo = "(unknown file)", 0, "(unknown function)",""
        if mode == 'many':
            self.procmanylog(modulename,msg)
            return
        else:
            self._log.error(msg,extra = {'modulename': sinfo})
        self.processlog(modulename,msg,mode)

    def findCaller(self, stack_info=False):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            '''
            if filename == _srcfile:
                f = f.f_back
                continue
            '''
            sinfo = None
            codeinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()

            if sinfo is not None:#tang do this
                codeinfo = sinfo.split("\n")
                if logfunc.index(codeinfo[-1].strip()[:6]) > -1:
                    sinfo  = codeinfo[-2].strip()+'()'    #如果使用lambd表达式则将表达式的函数不输出日志
                    print(sinfo)
                else:
                    sinfo  = codeinfo[-2].strip()+'()=>'+codeinfo[-1].strip()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break

        return rv

def main():
    setlog('gggglog.txt',DEBUG)
    lwarn('abscd','lambda')
    mlog.instance().warn('main','dddxxxxx')
    mlog.instance().error('main','EEEExxxxx')
    with open(__logpath__,'rt') as f:
        logtext = f.read()
    print(logtext)
if __name__ == '__main__':
    main()
