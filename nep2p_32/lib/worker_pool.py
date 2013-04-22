#from recode_worker import recode_worker
from util.singleton import Singleton
from util.internal_message import *
from util.message import *
import app_worker

@Singleton
class worker_pool(object):
	def __init__(self):
		self.pool = {}
		self.finished_worker = {}
		#self.recoder = recode_worker.recode_worker()
	
	@property
	def helper(self):
		return self.recoder
	
	@property
	def worker(self):
		return self.pool
	
	def get_worker(self, h):
		if h not in self.pool:
			self.pool[h] = app_worker.app_worker(h)
		return self.pool[h]
		
	def add_finished_worker(self, w):
		if w.myhash not in self.finished_worker:
			self.finished_worker[w.myhash] = w
	
	def give_pkt_to_helper(self, pkt):
		#recode any packet
		self.recoder.pkt_queue.put(pkt)


if __name__ == '__main__':
	w = worker_pool.Instance()
	print w.helper
	print w.worker
	w.worker['rgb'] = 1
	print w.worker['rgb']
	print w.worker

import recode_worker
