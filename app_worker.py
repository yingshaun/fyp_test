import random
import time
#import gevent, gevent.queue, gevent.socket
import tempfile, os
from util.config import *
from util.message import *
from util.internal_message import *
from util.common import printf, hashFunc
from util.logger import * 
#from util.cache import Cache, packetId
#from base_worker import base_worker
from util.bats import NIODecoder as Decoder
from util.bats import Encoder
import modules
import threading

from util.message import MessageType
from util.bmessage import *

class app_worker(object):
	def __init__(self, h):
		#base_worker.__init__(self)
		self.myhash = h
		self.mysize = 0

#encoder and decoder are initiallized when first needed
		self.encoder = None
		self.decoder = None

		##################################################
		#local_senders: from me to others
		#	key: asid | value: set of receivers (ip, asid)
		#remote_senders: from others to me
		#	key: asid | value: dict - (senders (ip, asid) -> (last update, last stop send))
		#	(since need to record last updated time to stop others)
		##################################################
		self.local_senders = {}
		self.remote_senders = {}
		self.decode_status = INITIALIZED

		############################################
		#for log use
		self.start_time = 0
		self.end_time = 0
		self.num_received = 0
		self.num_sent = 0
		self.logThread = None

		##################################################
		#send_buf: from me to others
		#	key: asid | value: Cached Python string of the message
		##################################################
		self.msg = message(message.create_message(MessageType.PACKET))
		self.send_pkt = self.msg.get_bm()
		self.send_pkt.file_hash = h
		self.send_buf = {}

	#call by IGW
	def init_encoder(self, filepath):
		if self.encoder == None:
			self.encoder = Encoder.fromfile(filepath)
			self.mysize = os.path.getsize(filepath)

	def init_decoder(self, filesize):
		if self.decoder == None:
			f = tempfile.mkstemp()
			self.decoder = Decoder.tofile(f[1], filesize, self.finish_callback, self.myhash)
			self.decoded_path = f[1]
			self.start_time = time.time()
			self.mysize = filesize

			#init the logger
			self.pktLogger = Logger('log/%s/%d.log'%(
				modules.ip.myip,
				self.mysize), 'a+')	# by Shaun
				#self.myhash),'a+')
			print 'a'
			self.logThread = AppLogger(self)
			print 'b'
			self.logThread.start()

	def init_send_header(self, local):
		if local in self.send_buf:
			return
		local_senders = self.local_senders[local]
		#:TODO: fixed 10 nodes for each packet no matter what
		#if len(local_senders)>10:
		#	local_senders = random.sample(local_senders, 9)
		#	local_senders.append(c.remote)
		sender_ip, sender_asid = list(self.remote_senders[local][SENDER])[0] if local in self.remote_senders and (0,0) in self.remote_senders[local] else (modules.ip.myip, local)
		self.send_pkt.file_size = self.mysize
		self.send_pkt.sender_addr = message.IPStringtoByte(sender_ip)
		self.send_pkt.sender_asid = sender_asid
		self.send_pkt.src_addr = message.IPStringtoByte(modules.ip.myip)
		self.send_pkt.src_asid = local
		self.send_pkt.dst_num = chr(len(local_senders))
		dst, self.send_pkt.dst_asid = \
			(list(t) for t in zip(*local_senders))
		#print 'local_senders', local_senders, 'dst', dst
		self.send_pkt.dst_addr = [message.IPStringtoByte(str(addr)) for addr in dst]
		self.send_buf[local] = 'nem  %s'%self.msg.get_head_buf()

	#call encoder to out goods
	def generate_pkt(self):
		if self.encoder == None:
			return
		#pkts = []
		#p = self.encoder.genPacket()
		#while p:
		#	pkts.append(p)
		#	p = self.encoder.genPacket()
		#self.num_sent += len(pkts)
		pkts = [self.encoder.genPacket() for i in xrange(16)]
		self.num_sent += 16
		return pkts

	#give packet to decoder
	#@profile
	def receive_pkt(self, pkt):
		if self.decoder == None:
			return
		#printf('hash=%s first bytes[%s] last bytes[%s]'%(hashFunc(pkt),pkt[:10],pkt[-10:]), 'receive_pkt', RED)
		self.decoder.receivePacket(pkt)
		self.num_received += 1

	def stop_sending_to_remote(self, local, remote):
		try:
			c = modules.connection_pool.get_connection(local, remote)
			c.remove_up_worker(self)
			printf("remove up_worker thing %s"%(c.up_worker,), "WARNING", YELLOW)
			if len(c.up_worker) == 0:
				modules.scheduler.unschedule_connection(c)
			self.local_senders[local].remove(remote)
		except Exception as e:
			print e
		if local in self.local_senders and len(self.local_senders[local]) == 0:
			del self.local_senders[local]
		self.completed_encode_check()

	#simliar to finish callback, this is called when a socket close, forced to close connection
	def stop_receiving_from_remote(self, local, remote):
		self.decode_status = WAITING_FIN
		modules.worker_pool.add_finished_worker(self)
		modules.connection_pool.get_connection(local, remote).down_worker.remove(self)
		modules.external_gateway.send_stop_message(self, local, remote)
		
	def finish_callback(self):
		self.finish_log()
		self.decode_status = WAITING_FIN
		modules.worker_pool.add_finished_worker(self)
		m = InternalMessage( \
				type=InternalMessageType.RECV_HEAD,
				recv_type=InternalMessageType.RECV_FILE,
				filepath=self.decoded_path,
		)
		for local, remote in self.remote_senders.iteritems():
			local_port = modules.bidict.get_port_from_asid(local)
			#send the received file to app
			if local_port != -1:
				m['senders'] = {a[0]:a[1] for a in remote[SENDER]}
				modules.internal_gateway.sock.sendto(
						m.encode(),
						('127.0.0.1', local_port),
				)

			for remote_addr in remote.iterkeys():
				if remote_addr == (0, 0):
					continue
				modules.connection_pool.get_connection(local, remote_addr).down_worker.remove(self)
				modules.external_gateway.send_stop_message(self, local, remote_addr)
				#still keep entry in remote_senders for recording update time

	def remove_expired_connection(self):
		temp1 = []
		for local, remote in self.remote_senders.iteritems():
			temp2 = []
			for remote_addr, time_info in remote.iteritems():
				if remote_addr == (0, 0):
					continue
				if (time.time() - time_info[0]) >= REAL_STOP_INTERVAL:
					temp2.append(remote_addr)
			for item in temp2:
				del remote[item]
			if len(remote) <= 1: #remote[(0, 0)] is for special use, so at least 1
				temp1.append(local)
		for item in temp1:
			del self.remote_senders[item]
		self.completed_decode_check()

	def completed_encode_check(self):
		if len(self.local_senders) == 0:
			self.encoder = None
			self.completed_all_check()

	def completed_decode_check(self):
		if len(self.remote_senders) == 0:
			try:
				del modules.worker_pool.finished_worker[self.myhash]
			except KeyError:
				pass
			self.decoder = None
			self.num_received = 0
			self.completed_all_check()

	def completed_all_check(self):
		if self.encoder == None and self.decoder == None:
			try:
				del modules.worker_pool.worker[self.myhash]
			except KeyError:
				pass

	##########################################################
	#for log use
	##########################################################
	def finish_log(self):
		if self.logThread:
			self.logThread.stop()
		#set end_time > 0 to trigger
		self.end_time = time.time()
		printf('\n\ttime_elapsed=%dsec\n\t#received=%d,#sent=%d,#decoded=%d'%(
			self.end_time-self.start_time,
			self.num_received,
			self.num_sent,
			self.decoder.getDecoded()
		), 'FINISHED', RED)
		try:
			os.mkdir('log')
		except:
			pass
		'''
		l = Logger('log/%d.log'%self.mysize)
		l.logline('%f\n%f\n%d\n%d\n%d'%(
			self.start_time,
			self.end_time,
			self.num_received,
			self.num_sent,
			self.decoder.getDecoded(),
		))
		'''
		l = Logger(LOG_FILE_BASE + 'gnl.json', 'w+')
		l.logline('{')
		l.logline('"start_time": %f,'%self.start_time)
		l.logline('"end_time": %f,'%self.end_time)
		l.logline('"duration": %d,'%(self.end_time - self.start_time))
		l.logline('"num_received": %d,'%self.num_received)
		l.logline('"num_sent": %d,'%self.num_sent)
		l.logline('"num_decoded": %d'%self.decoder.getDecoded())
		#l.logline('"hash_value": "%s"'%self.myhash)
		l.logline('}\n')
		l.close()
		"""
		l = dataFlowLogger('gnl.json')
		dd = dict()
		dd['start_time'] = self.start_time
		dd['end_time'] = self.end_time
		dd['duration'] = self.end_time - self.start_time
		dd['num_received'] = self.num_received
		dd['num_sent'] = self.num_sent
		dd['num_decoded'] = self.decoder.getDecoded()
		dd['hash_value'] = self.myhash
		l.logline(json.dumps(dd))
		l.close()
		"""

class AppLogger(threading.Thread):
	def __init__(self, app_worker):
		threading.Thread.__init__(self)
		self.app = app_worker
		self.stop_log = threading.Event()
		#print 'log init'

	def stop(self):
		self.stop_log.set()

	def run(self):
		try:
			print 'log start'
			while not self.stop_log.is_set():
				printf('%s sent: %d, rcvd: %d, decoded: %d'%(time.ctime()[11:19], self.app.num_sent, self.app.num_received, self.app.decoder.getDecoded() if self.app.decoder else 0), 'APP_WORKER', RED)
				self.app.pktLogger.logline("%f %d %d %d"%(
					time.time(),
					self.app.num_sent,
					self.app.num_received,
					self.app.decoder.getDecoded() if self.app.decoder else 0
				))
				time.sleep(PKTLOG_INTERVAL)
			self.app.pktLogger.logline("%f %d %d %d"%(
				time.time(),
				self.app.num_sent,
				self.app.num_received,
				self.app.decoder.getDecoded() if self.app.decoder else 0
			))
			self.app.pktLogger.close()
		except:
			pass
		print 'Logger stopped'
