import logging
import random, time
from util.common import *
from util.config import *
#from util.internal_message import *
from util.message import MessageType
from util.bmessage import *
#from util.node_list import NodeList
from util.singleton import Singleton
#import bintrees
import threading
import modules
from heapq import heappush, heappop, heapify, heappushpop
import struct
from util.logger import *

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

		self.myLogger = dataFlowLogger('snd.log')
		self.myLogger.start()

	def __del__(self):
		self.myLogger.stop()
	
	#@profile
	def run(self):
		myip = modules.ip.myip
		#w = None
		#send_pkt = Message(
		#		type=MessageType.PACKET,
		#		src_ip=myip,
		#)

		#msg = message(message.create_message(MessageType.PACKET))
		#send_pkt = msg.get_bm()
		#send_pkt.src_addr = message.IPStringtoByte(myip)
		last_sent = 0
		last_time = time.time()

		while 1:
			self.semaphore.acquire()
			self.semaphore.release()

			self.lock.acquire()

			# :TODO: workaround to block it...
			if len(self.connection_heap)>0 and self.connection_heap[0].next_send_time <= time.time():
				self.count += 1
				#c = heappop(self.connection_heap)
				#c.next_send_time += c.send_period
				#heappush(self.connection_heap, c)
				c = self.connection_heap[0]
				c.next_send_time += c.send_period #* 16# :TODO: hardcode
				#heappushpop(self.connection_heap, c)
				heappop(self.connection_heap)
				heappush(self.connection_heap, c)

				h, s, pkts = c.generate_pkt()
				#:TODO: simplified needed
				if pkts == None:
					sleep_period = self.connection_heap[0].next_send_time - time.time() - self.t
					self.lock.release()
					if sleep_period >= self.SLEEP_THRESHOLD: #:TODO: adjust threshold
						time.sleep(sleep_period)
						pass
					continue
				w = modules.worker_pool.get_worker(h)
				#			local = w.local_senders[c.local]
				#			print 'local:', local
				#			#:TODO: fixed 10 nodes for each packet no matter what
				#			if len(local)>10:
				#				local = random.sample(local, 9)
				#				local.append(c.remote)
				#			sender_ip, sender_asid = list(w.remote_senders[c.local][SENDER])[0] if c.local in w.remote_senders and (0,0) in w.remote_senders[c.local] else (myip, c.local)
				#send_pkt['hash']=h
				#send_pkt['size']=s
				#send_pkt['sender_ip']=sender_ip
				#send_pkt['sender_asid']=sender_asid
				#send_pkt['src_asid']=c.local
				#send_pkt['dst_addrs']={n[0]:n[1] for n in local}
				#			send_pkt.file_hash = h
				#			send_pkt.file_size = s
				#			send_pkt.sender_addr = message.IPStringtoByte(sender_ip)
				#			send_pkt.sender_asid = sender_asid
				#			send_pkt.src_asid = c.local
				#send_pkt['dst_addrs']={n[0]:n[1] for n in local}
				#			send_pkt.dst_num = chr(len(local))
				# :TODO: :(
				#send_pkt.dst_addr, send_pkt.dst_asid = \
				#	(list(t) for t in zip(*local))
				#			dst, send_pkt.dst_asid = \
				#				(list(t) for t in zip(*local))
				#			send_pkt.dst_addr = [message.IPStringtoByte(str(addr)) for addr in dst]
				ip = c.remote[0]
				ip_addr = (ip, EXTERNAL_PORT)
				#ip_addr = (ip, 34567)
				#print 'ip_addr', ip_addr

				for p in pkts:
					#send_pkt.payload = p
					#			msg.set_payload(p)
					#send_pkt['timestamp'] = time.time()
					#			send_pkt.timestamp = time.time()
					#ppp = send_pkt.encode()
					#			ppp = msg.dumps()
					#if len(ppp)>BUF_SIZE:
					#	printf("send pkt too long! %d"%(len(ppp),), "PKT", YELLOW)
					#ppp = "%s%17.6f%s"%(w.send_buf[c.local], time.time(), p)
					#ppp = ''.join([w.send_buf[c.local], "%17.6f"%time.time(), p])
					#:TODO:
					ppp = struct.pack('125sd1042s', w.send_buf[c.local], time.time(), p)
					modules.external_gateway.sock.sendto(ppp,ip_addr)
					#pass

				modules.external_gateway.node_list.updateSendTime(ip)
				c.num_sent += len(pkts)
				
				tmp_remote = (ip, c.local)	# (ip, asid) by Shaun
				self.myLogger.logPkt(tmp_remote, time.time(), len(pkts))

				#c.next_send_time += c.send_period
				#heappush(self.connection_heap, c)

				#:TODO: for batch send
				#c.next_send_time += c.send_period*len(pkts)
				#heappush(self.connection_heap, c)


				#if self.DEBUG:
				if self.DEBUG:
					now = time.time()
					#printf("time=%f asid=%d target=[%s,%d]\n\tnum_sent=%d num_recv=%d num_ack=%d decoded=%d\n\treceived=%d fillratio=%f\n\tsend(t,c)=%f,%f count=%d encode=%f\n\tdecode=%f process_pkt=%f generate=%f\n\ttime_elapsed=%f send_rate=%f"%(
					#now, c.local, ip, c.remote[1],
					#c.num_sent, c.num_received, c.num_ack, w.decoder.getDecoded() if w and w.decoder else 0,
					#w.decoder.getReceived() if w and w.decoder else 0, w.decoder.getBufferFillRatio() if w and w.decoder else 0,
					#self.t, self.send_time, self.count, self.encode_time,
					#modules.external_gateway.t3, modules.external_gateway.t2, self.generate_time,
					#now-c.start_time, c.num_sent/(now-c.start_time)), "SCHEDULER", RED)
					printf("time=%f asid=%d target=[%s,%d]\n\ttime_elapsed=%f send_rate=%f send_period=%f id=%d name=%s"%(
					now, c.local, ip, c.remote[1],
					now-c.start_time, (c.num_sent-last_sent)/(now-last_time), c.send_period, id(c), c.name), "SCHEDULER", RED)

					if c.num_sent-last_sent > 2000:
						last_sent = c.num_sent
						last_time = now
			
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

	def reschedule_connection(self, c):
		self.semaphore.acquire()
		self.lock.acquire()
		try:
			self.connection_heap.remove(c)
			heapify(self.connection_heap)
		except KeyError:
			logger.exception("unschedule in reschedule")

		c.max_bandwidth = c.send_rate
		c.send_period = 1.0 / c.max_bandwidth
		c.next_send_time = time.time() + c.send_period

		heappush(self.connection_heap, c)
		self.lock.release()
		self.semaphore.release()
