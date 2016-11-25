from socket import *
from socket import gethostbyname, gethostname
import struct


class UdpSocket:
    def __init__(self):
        self._address = None
        self._sock = None
        self._buffsize = 10000

    def set(self, local_ip, local_port, buffsize, groupaddress=INADDR_NONE):
        self._address = (local_ip, local_port)
        self._sock = socket(AF_INET, SOCK_DGRAM)
        self._buffsize = buffsize
        try:
            self._sock.setsockopt(SOL_SOCKET, SO_RCVBUF, self._buffsize)
            self._sock.setsockopt(SOL_SOCKET, SO_SNDBUF, self._buffsize)
            self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self._sock.setsockopt(SOL_SOCKET, IP_TTL, 2)
            self._sock.bind(self._address)
            print('bind success')
        except Exception as e:
            print('error %s' % e)
            return

        self._sock.settimeout(1)
        ttl = struct.pack('b', 2)

        if groupaddress is not INADDR_NONE:
            group = inet_aton(groupaddress)
            mrep = struct.pack('4sl', group, INADDR_ANY)
            self._sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
            self._sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mrep)
     
    def send(self, ip, port, data):
        self._sock.sendto(data, 0, (ip, port))
        # print('send %d bytes data = %s ip = %s port = %d' %(self._sock.sendto(data,0,(destip,destport)),data,destip,destport))

    def close(self):
        self._sock.close()

    def recv(self):
        try:
            data, peerip = self._sock.recvfrom(10000)
            if not data:
                return None, None
            else:
            # print('recv,%s'%data)
                return data, peerip
        except Exception as e:
            if ('%s' % e) != 'timed out':
                print('udpsocket error %s' % e)
            return None, None


def getlocalip():
    hostname = gethostname()
    localip = gethostbyname(hostname)
    return localip


def main():
    a = UdpSocket()
    a.set('192.170.41.210',24568,1000,'225.0.0.1')
#    a.send("225.0.0.1",24568,b'1223344')
    ip = ''
    data = b''
    ip,data = a.recv()
    a.close()
    print('exit send and close socket')
#main()



       

        
                        
                             
                             
                             
                             
