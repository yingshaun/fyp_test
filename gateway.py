import logging
import time
import socket
#import rudp
import json
from util.common import printf
from util.config import *
import threading
#from util.message import Message
from util.message import MessageType
from util.bmessage import *

class gateway(threading.Thread):
	#t3 = 0
	def __init__(self):
		threading.Thread.__init__(self)
		self.BUFFERMODIFIED = conf['buffermodified'] if 'buffermodified' in conf else true
		self.BUFFERSIZE = conf['buffersize'] if 'buffersize' in conf else 3 * 1024 * 1024
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		#self.sock = rudp.rudpSocket()
		if self.BUFFERMODIFIED:
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFFERSIZE)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.BUFFERSIZE)
		#self.a = True
		self.start_time = 0
		self.FLOOD = conf['flood'] if 'flood' in conf else False
		self.DEBUG = conf['scheduler_debug'] if 'scheduler_debug' in conf else True
	
	def run(self):
		self.sock.bind((self.ip, self.port))
		msg = message(message.create_message(MessageType.PACKET))
		send_pkt = msg.get_bm()
		while True:
			try:
				#t = time.clock()
				(pkt, client) = self.sock.recvfrom(BUF_SIZE)
				#ttt = time.clock()
				#if a:
				#	self.start_time = time.clock()
				#	a = False
				#self.t = time.clock() - self.start_time
				#if pkt[:5].strip() == Message.HEAD:
				if pkt[:5] == 'nem  ':
					#pkt = Message.decode(pkt)
					msg.loads(pkt[5:])
					send_pkt.timestamp = time.time() - send_pkt.timestamp
					self.process_pkt(msg)
					#if pkt == None:
					#	continue
					#if 'timestamp' in pkt:
					#	pkt['timestamp'] = time.time() - pkt['timestamp']
				else:
					#internal message
					if self.FLOOD:
						print 'gateway pkt', pkt, client
					pkt = json.loads(pkt)
					pkt['src_ip'] = client[0]
					pkt['src_port'] = client[1]
					self.process_pkt(pkt)
				#self.t3 = (self.t3+time.clock()-t)/2 if self.t3!=0 else time.clock()-t
			except Exception, e:
				logging.exception("gateway!!")
			#printf("t=%f"%(gateway.t), "gateway", RED)
		
	def process_pkt(self, pkt):
		raise NotImplementedError('I am abstract')
