import gevent, gevent.socket
#import rudp
import json
import tempfile, os
from util.config import *
from util.internal_message import *

class AppSocket(object):
	EXTERNAL_PORT = 33333

	def __init__(self):
		pkt = {}
		pkt['type'] = InternalMessageType.HI
		self._local = ('127.0.0.1', INTERNAL_PORT)
		self._sock = gevent.socket.socket(gevent.socket.AF_INET, gevent.socket.SOCK_DGRAM, gevent.socket.IPPROTO_UDP)
		#self._sock = rudp.rudpSocket()
		self._sock.sendto(json.dumps(pkt), self._local)
	
	def bind(self, asid):
		pkt = {}
		pkt['type'] = InternalMessageType.BIND
		pkt['asid'] = asid
		self._sock.sendto(json.dumps(pkt), self._local)

		#On success, zero is returned. On error, -1 is returned, and nothing is set appropriately
		ret_pkt = json.loads(self._sock.recv(BUF_SIZE))
		print ret_pkt
		return ret_pkt['val'] if ret_pkt['type'] == InternalMessageType.RETURN else -1

	def send(self, msg):
		#wrap sendto
		pass

	def sendto(self, addrs, msg):
		'''
			addrs: list of address+ip pairs
			msg: message to send to the receivers
		'''
		resolved_addrs = [(self._resolve_dns(addr[0]),addr[1]) for addr in addrs]
		pkt = {}
		pkt['type'] = InternalMessageType.SEND_HEAD
		pkt['send_type'] = InternalMessageType.SEND
		pkt['dst_addrs'] = {a[0]:a[1] for a in resolved_addrs if a[0] != ''}
		pkt['content'] = msg
		self._sock.sendto(json.dumps(pkt), self._local)

		ret_pkt = json.loads(self._sock.recv(BUF_SIZE))
		return ret_pkt['val'] if ret_pkt['type'] == InternalMessageType.RETURN else -1
	
	def sendfile(self, addrs, filepath):
		pass

	def sendfileto(self, addrs, filepath):
		resolved_addrs = [(self._resolve_dns(addr[0]),addr[1]) for addr in addrs]
		pkt = {}
		pkt['type'] = InternalMessageType.SEND_HEAD
		pkt['send_type'] = InternalMessageType.SEND_FILE
		pkt['dst_addrs'] = {a[0]:a[1] for a in resolved_addrs if a[0] != ''}
		pkt['filepath'] = filepath
		self._sock.sendto(json.dumps(pkt), self._local)

		ret_pkt = json.loads(self._sock.recv(BUF_SIZE))
		return ret_pkt['val'] if ret_pkt['type'] == InternalMessageType.RETURN else -1

	def recv(self):
		#wrap recvfrom
		pass
	
	def recvfrom(self):
		pkt = json.loads(self._sock.recv(BUF_SIZE))
		if pkt['type'] == InternalMessageType.RECV_HEAD:
			addrs = [(k,v) for k,v in pkt['senders'].iteritems()]
			if pkt['recv_type'] == InternalMessageType.RECV_FILE:
				data = open(pkt['filepath']).read()
				os.remove(pkt['filepath'])
				return addrs,data
			#elif pkt['recv_type'] == InternalMessageType.RECV:
		return None
	
	def precache(self, pkt):
		pass

	def close(self):
		pkt = {}
		pkt['type'] = InternalMessageType.BYE
		self._sock.sendto(json.dumps(pkt), self._local)

		ret_pkt = json.loads(self._sock.recv(BUF_SIZE))
		self._sock.close()
		return ret_pkt['val'] if ret_pkt['type'] == InternalMessageType.RETURN else -1

	def _resolve_dns(self, ip):
		'''
			ip: a domain name or IP
		'''
		try:
			l = gevent.socket.getaddrinfo(ip, EXTERNAL_PORT, socktype=gevent.socket.SOCK_DGRAM)
		except gevent.socket.gaierror:
			return ''
		print 'resolve_dns', l[0][4][0]
		return l[0][4][0] if len(l)>0 else ''

if __name__ == "__main__":
	sock = AppSocket()
	print sock._resolve_dns("dev.nep2p.com")
	print sock._resolve_dns("")
	print sock._resolve_dns("192.168.84.208")
	#sock.sendto([("dev.nep2p.com",333), ("192.168.84.208", 421), ("localhost", 3342), ("", 30933)], 'hi')
