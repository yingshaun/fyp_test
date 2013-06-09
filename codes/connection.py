#import logging
import random, time, sys
from util.config import *
from util.message import *
from util.internal_message import *
from util.common import printf
from util.logger import Logger
from util.congestion import Congestion
from threading import Lock
import modules

class connection(object, Congestion):
	def __init__(self, local = 0, remote = ('127.0.0.1', 0), max_bandwidth = 1000, name = ''):
		self.name = name #debug use
		self.local = local
		self.remote = remote

		Congestion.__init__(self)
		self.send_rate = max_bandwidth

		self.max_bandwidth = max_bandwidth
		self.send_period = 1.0 / self.max_bandwidth
		self.next_send_time = sys.maxint

		self.up_worker = set()
		self.up_worker_list = []
		self.up_worker_current = 0
		self.up_worker_modified = True

		self.down_worker = set()

		self.pkt_list = dict() #{hash:[pkts]}
		self.pkt_lock = Lock()
		self.FLOOD = conf['flood'] if 'flood' in conf else False
		self.BATCH = conf['batch_send'] if 'batch_send' in conf else False
		self.start_time = time.time()

		self.current_h = ''
		self.current_s = 0
		self.current_pkts = []

	def change_max_bandwidth(self):
		try:
			#if Congestion.change_max_bandwidth(self):
			if abs(self.send_rate-self.max_bandwidth) > self.max_bandwidth*Congestion.THRESHOLD:
				if modules.scheduler.connection_scheduled(self):
					#modules.scheduler.unschedule_connection(self)
					#self.max_bandwidth = self.send_rate
					#self.send_period = 1.0 / self.max_bandwidth
					#modules.scheduler.schedule_connection(self)
					modules.scheduler.reschedule_connection(self)
				else:
					self.max_bandwidth = self.send_rate
					self.send_period = 1.0 / self.max_bandwidth
		except Exception, e:
			#logging.exception("change_max_bandwidth failed")
			print e
			pass
	
	def add_up_worker(self, w):
		self.up_worker.add(w)
		self.up_worker_modified = True
	
	def remove_up_worker(self, w):
		self.up_worker.remove(w)
		self.up_worker_modified = True

	def add_pkt(self, filehash, payload):
		#self.pkt_lock.acquire()
		if filehash not in self.pkt_list:
			self.pkt_list[filehash] = [payload]
		else:
			self.pkt_list[filehash].append(payload)
		#self.pkt_lock.release()

	def generate_pkt(self):
		if self.current_pkts:
			pkt = self.current_pkts[0]
			self.current_pkts = self.current_pkts[1:]
			return (self.current_h, self.current_s, [pkt])

		#rebuild the list if worker set is modified
		if self.up_worker_modified:
			self.up_worker_list = list(self.up_worker)
			random.shuffle(self.up_worker_list)
			self.up_worker_modified = False
			self.up_worker_current = 0

		#print len(self.up_worker_list), self.up_worker_current
		#:TODO: just a workaround
		try:
			w = self.up_worker_list[self.up_worker_current]
		except:
			#:TODO: wasted one cycle and to know that this worker doesn't have pkts to send
			#self.up_worker_current = self.up_worker_current + 1 if self.up_worker_current < len(self.up_worker_list) - 1 else 0
			return ('',0,None)
		h = w.myhash
		s = w.mysize

		#:TODO:
		#if there are pkts to broadcast, return those pkts=BATCH_SIZE
		#self.pkt_lock.acquire()
		pkt = None
		if h in self.pkt_list:
			if len(self.pkt_list[h])>BATCH_SIZE:
				pkt = self.pkt_list[h][:BATCH_SIZE]
				self.pkt_list[h] = self.pkt_list[h][BATCH_SIZE:]
			else:
				pkt = self.pkt_list[h]
				del self.pkt_list[h]
			w.num_sent += len(pkt)
		else:
			#:TODO: if encoder==None, return None
			pkt = w.generate_pkt()
		#self.pkt_lock.release()
		self.up_worker_current = (self.up_worker_current + 1) % len(self.up_worker_list)
		if pkt == None:
			return ('',0,None)
		
		#:TODO: return just 1 pkt @ call
		if self.BATCH:
			self.current_h,self.current_s,self.current_pkts = (h, s, pkt[1:])
			return (h,s,[pkt[0]])
		else:
			return (h, s, pkt)


	def __eq__(self, other):
		return id(self) == id(other)

	def __cmp__(self, other):
		ret = self.next_send_time - other.next_send_time
		return ret if ret else id(self) - id(other)

if __name__ == '__main__':
	l = []
