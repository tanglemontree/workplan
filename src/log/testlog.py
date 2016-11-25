# -*- coding:utf-8 -*-
__author__ = 'twt'
'''
if __name__ == '__main__':
    import os,sys
    mm = os.getcwd()
    mm = os.path.normpath(mm)
    dirs = mm.split(os.sep)
    curdir = mm.replace(dirs[-1],'')
    sys.path.append(curdir)
    print(sys.path)
'''
if __name__ == '__main__':
    import os,sys
    cur = os.path.abspath(os.path.dirname('__file__'))
    mm = os.path.normpath(cur)
    dirs = mm.split(os.sep)
    curdir = mm.replace(dirs[-1],'')
    print(curdir)
    print(os.sep)
    curdir = curdir[:-1]

    sys.path[0] = ''
    sys.path.append(curdir)
    print(sys.path)
#    print(cur)
from log import a,lwarn#（在包外调用时没问题的）
#from . import a,lwarn   在直接调用testlog.py时此种方法会出错，而from log import a没问题
print(a)
lwarn('ddd','dddd')


