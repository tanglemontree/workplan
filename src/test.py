#from log import DEBUG
#from base import appdefine
from base import mpath

print(mpath.inistance().getroot())
print(mpath.inistance().getlogpath())
c = mpath.inistance().getconfigpath()
c = 'c:1.txt'
print(mpath.inistance().getconfigpath())
from user import usermng,user

cuser = user()
cuser.name = 'tang'
cuser.online = True
usermng.instance().add(cuser)
puser = cuser
cuser.name = 'li'
cuser.nickname = 'loe'
usermng.instance().add(cuser)
usermng.instance().writetofile()
c = usermng.instance()

#s = dir()
#import sys
#print(sys.path)
#from log import testlog
# #import base.appdefine
#import log.testlog

#from net import netmng

#from net import psocket

