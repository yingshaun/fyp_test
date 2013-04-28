import logging
import random, time
from util.common import *
from util.config import *
#from util.internal_message import *
from util.message import *
#from util.node_list import NodeList
from util.singleton import Singleton
from util.logger import Logger
#import bintrees
import threading
import modules
from heapq import heappush, heappop, heapify

@Singleton
class scheduler(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.connection_heap = []
		self.lock = threading.Lock()
		self.semaphore = threading.Semaphore(0)

		self.schedule_time = 0
		self.send_time = 0
		self.encode_time = 0
		self.generate_time = 0

		self.t = 0 #used for checking the time for 
		#self.SLEEP = conf['scheduler_sleep'] if 'scheduler_sleep' in conf else True
		self.DEBUG = conf['scheduler_debug'] if 'scheduler_debug' in conf else True
		#self.SEND_RATIO = conf['scheduler_sendratio'] if 'scheduler_sendratio' in conf else 0.85
		#self.SEND_BOUND = conf['scheduler_sendbound'] if 'scheduler_sendbound' in conf else 500
		self.SLEEP_THRESHOLD = conf['scheduler_sleepthreshold'] if 'scheduler_sleepthreshold' in conf else 0
		#self.FLOOD = conf['flood'] if 'flood' in conf else False
		self.count = 0

		###############################################################################	
		self.myLogger = Logger('log/snd_' + str(time.time()))
		self.myLogger.logline('# Start of logging: ' + time.ctime())
		#self.myCount = (0, (u'0', 0), 0)	# (timestamp, (ip, asid), count)
		self.myCount = dict()			# {(ip, asid): (timestamp, count)}
		###############################################################################


	###############################################################################
	def __del__(self):
		#self.myLogger.logline(str(self.myCount))
		for tmp_remote in self.myCount.keys():
			myCurCount = self.myCount[tmp_remote]
                        self.myLogger.logline('{0}; {1}; {2}'.format(tmp_remote, myCurCount[0], myCurCount[1]))
                self.myLogger.logline('# End of logging: ' + time.ctime())
                self.myLogger.close()
	###############################################################################

	def run(self):
		myip = modules.ip.myip
		#w = None
		send_pkt = Message(
				type=MessageType.PACKET,
				src_ip=myip,
		)

		while True:
			self.semaphore.acquire()
			self.semaphore.release()

			self.lock.acquire()

			t = time.time()
			if self.connection_heap[0].next_send_time <= time.time():
				self.count += 1
				c = heappop(self.connection_heap)

				tt = time.clock()
				h, s, pkts = c.generate_pkt()
				self.generate_time += time.clock() -tt
				#:TODO: simplified needed
				if pkts == None:
					c.next_send_time += c.send_period
					heappush(self.connection_heap, c)
					sleep_period = self.connection_heap[0].next_send_time - time.time() - self.t
					self.lock.release()
					if sleep_period >= self.SLEEP_THRESHOLD: #:TODO: adjust threshold
						time.sleep(sleep_period)
					continue
				w = modules.worker_pool.get_worker(h)
				local = w.local_senders[c.local]
				#:TODO: fixed 10 nodes for each packet no matter what
				if len(local)>10:
					local = random.sample(local, 9)
					local.append(c.remote)
				sender_ip, sender_asid = list(w.remote_senders[c.local][SENDER])[0] if c.local in w.remote_senders and (0,0) in w.remote_senders[c.local] else (myip, c.local)
				send_pkt['hash']=h
				send_pkt['size']=s
				send_pkt['sender_ip']=sender_ip
				send_pkt['sender_asid']=sender_asid
				send_pkt['src_asid']=c.local
				send_pkt['dst_addrs']={n[0]:n[1] for n in local}
				ip = c.remote[0]


				for p in pkts:
					send_pkt.payload = p
					send_pkt['timestamp'] = time.time()
					tt = time.clock()
					ppp = send_pkt.encode()
					self.encode_time += time.clock() -tt
					#if len(ppp)>BUF_SIZE:
					#	printf("send pkt too long! %d"%(len(ppp),), "PKT", YELLOW)
					modules.external_gateway.sock.sendto(ppp,(ip,EXTERNAL_PORT))

				#################################################################################################
					#print len(str(ppp))
					#self.myLogger.logline('{0}, {1}, {2}'.format(time.time(), (ip, send_pkt['src_asid']), len(str(ppp))))
				tmp_remote = (ip, send_pkt['src_asid'])
				#curTime = float('%0.1f'%time.time())	# Precision: 0.01 seconds
				curTime = int(time.time())	# Precision: 1 seconds

				myCurCount = self.myCount.get(tmp_remote)
				if myCurCount == None:
					self.myCount[tmp_remote] = (curTime, len(pkts))
				elif curTime == myCurCount[0]:
					self.myCount[tmp_remote] = (curTime, myCurCount[1] + len(pkts))
				else:
					self.myLogger.logline('{0}; {1}; {2}'.format(tmp_remote, myCurCount[0], myCurCount[1]))
					self.myCount[tmp_remote] = (curTime, len(pkts))

				#if curTime == self.myCount[0] and tmp_remote == self.myCount[1]:
				#	self.myCount = (self.myCount[0], self.myCount[1], self.myCount[2] + len(pkts))
				#	print self.myCount
				#else:
				#	self.myLogger.logline(str(self.myCount))
				#	self.myCount = (curTime, tmp_remote, len(pkts))
				##################################################################################################

				modules.external_gateway.node_list.updateSendTime(ip)
				c.num_sent += len(pkts)
				#c.next_send_time += c.send_period
				#heappush(self.connection_heap, c)

				#:TODO: for batch send
				c.next_send_time += c.send_period*len(pkts)
				heappush(self.connection_heap, c)

				self.t = (self.t+time.time()-t)/2 if self.t else time.time()-t
				self.send_time += time.time()-t

				if self.DEBUG:
					now = time.time()
					printf("time=%f asid=%d target=[%s,%d]\n\tnum_sent=%d num_recv=%d num_ack=%d decoded=%d\n\treceived=%d fillratio=%f\n\tsend(t,c)=%f,%f count=%d encode=%f\n\tdecode=%f process_pkt=%f generate=%f\n\ttime_elapsed=%f send_rate=%f"%(
					now, c.local, ip, c.remote[1],
					c.num_sent, c.num_received, c.num_ack, w.decoder.getDecoded() if w and w.decoder else 0,
					w.decoder.getReceived() if w and w.decoder else 0, w.decoder.getBufferFillRatio() if w and w.decoder else 0,
					self.t, self.send_time, self.count, self.encode_time,
					modules.external_gateway.t3, modules.external_gateway.t2, self.generate_time,
					now-c.start_time, c.num_sent/(now-c.start_time)), "SCHEDULER", RED)
			
			sleep_period = self.connection_heap[0].next_send_time - time.time() - self.t
			if sleep_period >= self.SLEEP_THRESHOLD: #TODO: adjust threshold
				if self.DEBUG:
					printf("sleep_period=%f"%(sleep_period), "SCHEDULER", RED)
				self.lock.release()
				time.sleep(sleep_period)
			else:
				self.lock.release()



	def connection_scheduled(self, c):
		self.lock.acquire()
		ret = c in self.connection_heap
		self.lock.release()
		return ret

	def schedule_connection(self, c):
		self.lock.acquire()
		c.next_send_time = time.time() + c.send_period
		heappush(self.connection_heap, c)
		self.lock.release()
		self.semaphore.release()
	
	def unschedule_connection(self, c):
		self.semaphore.acquire()
		self.lock.acquire()
		try:
			self.connection_heap.remove(c)
			heapify(self.connection_heap)
		except KeyError:
			logger.exception("unschedule")
		self.lock.release()
