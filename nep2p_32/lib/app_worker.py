import random
import time
#import gevent, gevent.queue, gevent.socket
import tempfile, os
from util.config import *
from util.message import *
from util.internal_message import *
from util.common import printf, hashFunc
from util.logger import Logger
#from util.cache import Cache, packetId
#from base_worker import base_worker
from util.bats import NIODecoder as Decoder
from util.bats import Encoder
import modules
import threading

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

		############################################

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
			self.pktLogger = Logger('log/%s/%d/%s.log'%(
				modules.ip.myip,
				self.mysize,
				self.myhash),'a+')
			print 'a'
			self.logThread = AppLogger(self)
			print 'b'
			self.logThread.start()

	#call encoder to out goods
	def generate_pkt(self):
		if self.encoder == None:
			return
		pkts = []
		p = self.encoder.genPacket()
		while p:
			pkts.append(p)
			p = self.encoder.genPacket()
		self.num_sent += len(pkts)
		return pkts

	#give packet to decoder
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
		l = Logger('log/%d.log'%self.mysize)
		l.logline('%f\n%f\n%d\n%d\n%d'%(
			self.start_time,
			self.end_time,
			self.num_received,
			self.num_sent,
			self.decoder.getDecoded(),
		))
		l.close()

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
