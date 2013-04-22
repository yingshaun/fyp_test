import sys

import gevent, gevent.queue, gevent.socket, time
from util.bats import Recoder
from util.config import *
from util.common import packetId
from base_worker import base_worker
from util.message import *
from util.internal_message import *
from util.ip import IP
import external_gateway as egw
#from util.cache import Cache, packetId

class recode_worker(base_worker):
	def __init__(self):
		base_worker.__init__(self)
		#self.internal_port = 0
		self.asid = HELPER_ASID
		#helper related
		self.recoder_dict = {} #{hash:recoder}
		self.recoder = Recoder()
		self.coded_buffer = {} #{hash:{id:{id,packets,num,timestamp}}}

	def add_pkt(self, hashValue, coded_pkt):
		if hashValue not in self.coded_buffer:
			self.coded_buffer[hashValue] = {}
		t = self.coded_buffer[hashValue]
		pid = packetId(coded_pkt)
		if pid not in t:
			t[pid] = {
				'id': pid,
				'packets':coded_pkt,
				'num':1,
				'timestamp':time.time()
			}
			t = t[pid]
		else:
			t = t[pid]
			t['packets'] += coded_pkt
			t['num'] += 1
			t['timestamp'] = time.time()
		return t

	def del_pkts(self, hashValue, pid):
		if hashValue in self.coded_buffer and \
				pid in self.coded_buffer[hashValue]:
			del self.coded_buffer[hashValue][pid]

	def send_pkts(self, hashValue, cbuffer, msg, count=1):
		#recode and send to neighbours
		#recoder = self.recoder_dict[hashValue]
		m = InternalMessage( \
				type=InternalMessageType.RECODE_PACKETS,
				hash=hashValue,
				src_ip=IP.Instance().myip,
				src_asid=HELPER_ASID,
		)
		m['size'] = msg['size']
		m['sender_ip']=msg['sender_ip']
		m['sender_asid']=msg['sender_asid']
		m['dst_addrs']=msg['dst_addrs']
		m.payload = [self.recoder.genPacket(
				cbuffer['packets'],
				cbuffer['num']
		) for i in xrange(count)]
		egw.external_gateway.Instance().pkt_queue.put(m)
		#drop, because of the store-and-forward policy
		if cbuffer['num'] >= BATCH_SIZE:
			self.del_pkts(hashValue, cbuffer['id'])

	def send_pkt(self, msg):
		#send to neighbours directly
		m = InternalMessage( \
				type=InternalMessageType.RECODE_PACKETS,
				hash=msg['hash'],
				src_ip=IP.Instance().myip,
				src_asid=HELPER_ASID,
				size=msg['size'],
				sender_ip=msg['sender_ip'],
				sender_asid=msg['sender_asid'],
				dst_addrs=msg['dst_addrs'],
		)
		m.payload = [msg.payload[:]]
		egw.external_gateway.Instance().pkt_queue.put(m)

	def process_queue_pkt(self, pkt):
		'''
			pkt: dict
		'''
		if MessageType.isValid(pkt['type']):
			#msg = Message.decode_dict(pkt)
			msg = pkt
			if msg['type'] == MessageType.PACKET and 'to_all' not in msg:
				self.send_pkt(msg)
				#:TODO: skip all the recoding first
				#cbuffer = self.add_pkt(msg['hash'], msg.payload)
				##:TODO: append last msg
				#cbuffer['last_msg'] = pkt
				#self.send_pkts(msg['hash'], cbuffer, pkt)

	def regular_action(self):
		for hashValue,b in self.coded_buffer.iteritems():
			for pkts in b.itervalues():
				if pkts['timestamp']+RECODE_INTERVAL<time.time():
					#if timeout: send+delete
					self.send_pkts(hashValue, pkts, BATCH_SIZE-pkts['num'], pkts['last_msg'])
					self.del_pkts(hashValue, pkts['id'])

if __name__ == "__main__":
	r = recode_worker()
