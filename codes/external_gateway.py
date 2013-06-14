#import logging
import random, time
from util.common import *
from util.config import *
#from util.internal_message import *
from util.message import MessageType
from util.bmessage import *
from util.node_list import NodeList
from util.singleton import Singleton
import gateway
import modules
import cffi
from util.logger import *

ffi = cffi.FFI()

@Singleton
class external_gateway(gateway.gateway):
	def __init__(self):
		gateway.gateway.__init__(self)
		self.ip = '0.0.0.0'
		self.port = EXTERNAL_PORT

		self.node_list = NodeList()
		self.myip = modules.ip.myip

		self.sock_count = 0
		self.schedule_count = 0
		self.sock_time = 0
		self.schedule_time = 0

		self.decode_time = 0
		self.msg_decode_time = 0
		self.ack_time = 0
		self.ttt = 0

		self.FLOOD = conf['flood'] if 'flood' in conf else False
		self.STOP_DECODER = conf['stop_decoder'] if 'stop_decoder' in conf else False
		self.NO_PROCESS = conf['egw_noprocess'] if 'egw_noprocess' in conf else False
		self.stop_msg = message(message.create_message(MessageType.STOP))
		self.stop_pkt = self.stop_msg.get_bm()
		self.stop_pkt.src_addr = message.IPStringtoByte(self.myip)
	
		self.myLogger = dataFlowLogger('rcv.log')	# shaun
		self.myLogger.start()	# shaun
		self.controlMsgCount = 0	# shaun

	def __del__(self):	# shaun
		self.myLogger.stop()
		self.msgLogger = dataFlowLogger('msg.json')
		d = {"controlMsgCount": self.controlMsgCount}
		self.msgLogger.logline(json.dumps(d))
		self.msgLogger.close()

	#@profile
	def process_pkt(self, msg):
		if self.NO_PROCESS:
			return
		
		pkt = msg.get_bm()
		#print len(msg.dumps())
		#process the packets
		#check validity of message
		if not MessageType.isValid(ord(pkt.msg_type)):
			return
		#pkt = Message.decode_dict(pkt)
		#print 'pkt', pkt
		src = message.IPBytetoString(pkt.src_addr), pkt.src_asid

		#node list keep alive
		#self.node_list.updateRecvTime(pkt['src_ip'])
		self.node_list.updateRecvTime(src[0])

		dst_addrs = {message.IPBytetoString(pkt.dst_addr[i]):pkt.dst_asid[i] for i in xrange(ord(pkt.dst_num))}
		try:
			#local = pkt['dst_addrs'][self.myip]
			local = dst_addrs[self.myip]
		except KeyError:
			raise Exception("Couldn't find in dst_addrs")
			local = 0
			if 'dst_addrs' in pkt:
				printf("Can't find self %s in dst_addrs(%s)"%(self.myip,pkt['dst_addrs']), 'process local', YELLOW)
			else:
				printf("%s"%(pkt,), "process local", YELLOW)
		#remote = (pkt['src_ip'], pkt['src_asid'])
		#src = remote = message.IPBytetoString(pkt.src_addr), pkt.src_asid
		filehash = ffi.buffer(pkt.file_hash)[0:32]
		remote = src
		sender = message.IPBytetoString(pkt.sender_addr), pkt.sender_asid
		#w = modules.worker_pool.get_worker(pkt.file_hash[:]) if 'hash' in pkt else None
		w = modules.worker_pool.get_worker(filehash)
		send_to_me = True if (self.myip in dst_addrs and modules.bidict.asid_exist(dst_addrs[self.myip])) else False
		#printf("send_to_me=%d pkt_type=%d PKT=%d"%(send_to_me,pkt['type'],MessageType.PACKET), "recv", BLUE)
		
		if ord(pkt.msg_type) != MessageType.PACKET: self.controlMsgCount += 1 	# shaun

		if ord(pkt.msg_type) == MessageType.PACKET:
			if send_to_me == True:
				self.myLogger.logPkt(remote, time.time(), 1)	# shaun
				#get the worker and init its decoder (similar to that in IGW)
				w.init_decoder(pkt.file_size)
				if local not in w.remote_senders:
					w.remote_senders[local] = {}
					#:REFINE: complete real sender part
					w.remote_senders[local][(0, 0)] = set()
					w.remote_senders[local][(0, 0)].add((message.IPBytetoString(pkt.sender_addr),pkt.sender_asid))

				#update the keep alive time of this connection
				c = modules.connection_pool.get_connection(local, remote)
				c.down_worker.add(w)
				if remote not in w.remote_senders[local]:
					w.remote_senders[local][remote] = (0, 0)
				w.remote_senders[local][remote] = (time.time(), w.remote_senders[local][remote][1])

				#append a new packet for sending ack
				modules.batch_acknowledger.add(local, remote, pkt.timestamp)

				p = msg.get_payload()
				#print 'pkt', pkt
				#do different things with different status
				#if WAITING_FIN, remote side may lost the stop message, so send it again
				if w.decode_status == INITIALIZED:
					w.decode_status = DECODING
				if w.decode_status == DECODING:
					#printf('payload length=%d'%(len(pkt.payload)),'PACKET', GREEN)
					if not self.STOP_DECODER:
						#w.receive_pkt(pkt.get_payload())
						w.receive_pkt(p)
					#if random.randint(1, 800) == 1:
					#	printf('num_sent=%d num_received=%d time=%f'%(w.num_sent,w.num_received, time.time()),'PACKET', GREEN)
					c.num_received += 1
				elif w.decode_status == WAITING_FIN:
					self.send_stop_message(w, local, remote)

				#:TODO:
				#connection_pool.to_helper(pkt)
				#:REFINE: maybe done in helper?
				#send the pkt to others
				if sender[0] == src[0] and \
						sender[1] == src[1] and \
						src[0] != self.myip:
					#pkt.src_addr = message.IPStringtoByte(self.myip)
					#pkt.src_asid = local
					#pkt.timestamp = time.time()

					if local not in w.local_senders:
						w.local_senders[local] = set()
					old_dst_len = len(w.local_senders[local])
					for ip,asid in dst_addrs.iteritems():
						if ip == self.myip or ip == src[0] or ip == sender[0]:
							continue
						cc = modules.connection_pool.get_connection(local, (ip,asid))
						if w not in cc.up_worker:
							cc.add_up_worker(w)
						w.local_senders[local].add((ip,asid))
					if len(w.local_senders[local]) != old_dst_len:
						w.init_send_header(local)

					for ip,asid in dst_addrs.iteritems():
						if ip == self.myip:
							continue
						cc = modules.connection_pool.get_connection(local, (ip,asid))
						try:
							#cc.add_pkt(pkt.filehash[:], p)
							#printf("Added pkt [%s]"%filehash, "add_pkt", RED)
							cc.add_pkt(filehash, p)
						except Exception, e:
							#logging.exception("add_pkt!?")
							print "Failed add_pkt", e
							#pass
						if not modules.scheduler.connection_scheduled(cc):
							#print 'schedule', local, (ip,asid)
							modules.scheduler.schedule_connection(cc)
						#if self.FLOOD:
						#	print 'no add_pkt done'
						#self.sock.sendto(pkt.encode(), (ip,EXTERNAL_PORT))
						#:TODO: add back the app_worker.num_sent
						#w.num_sent += 1
						#c.num_sent += 1
			#else give it to helper
			#else:
			#	pass

		elif ord(pkt.msg_type) == MessageType.ACK:
			#printf('%s %s'%(local,remote),"ACK", RED)
			c = modules.connection_pool.get_connection(local, remote)
			#p = pkt.get_payload()
			#if self.DEBUG:
			#	printf(','.join([`ord(c)` for c in p[0:len(p)]]), "ACK", RED)
			try:
				#c.on_acknowledgement(pkt.data.split(','))
				#				c.on_acknowledgement(pkt.get_payload())
				#modules.connection_pool.get_connection(local, remote).on_acknowledgement(msg.get_payload())
				c.on_acknowledgement(msg.get_payload())
				c.change_max_bandwidth()
			except Exception, e:
				#logging.exception("on_ack failed")
				print 'ack', e
				pass

		elif ord(pkt.msg_type) == MessageType.STOP:
			if send_to_me == True:
				printf("STOP received: %s %s"%(local,remote), "WARNING", YELLOW)
				w.stop_sending_to_remote(local, remote)

			#TODO: how about helper
			#give the packet to worker pool and helper
			#self.worker_pool.give_pkt_to_helper(pkt)

		elif ord(pkt.msg_type) == MessageType.STATUS or ord(pkt.msg_type) == MessageType.KEEPALIVE:
			#:REFINE: update node list
			self.node_list.updateRecvTime(src[0])


	def regular_action(self):
		while True:
			#send keep alive if haven't sent for too long
			send_list = self.node_list.regular()
			if send_list:
				m = Message(
					type=MessageType.KEEPALIVE,
					src_ip=self.myip,
					src_asid=0,
				)
				for ip in send_list:
					m['dst_addrs'] = {ip:0}
					self.sock.sendto(m.encode(), (ip,EXTERNAL_PORT))
					self.node_list.updateSendTime(ip)
			#gevent.sleep(REGULAR_INTERVAL)
	
	def send_stop_message(self, w, local, remote):
		h = w.myhash
		local_ip = self.myip
		local_asid = local
		remote_ip = remote[0]
		remote_asid = remote[1]
		if time.time() - w.remote_senders[local][remote][1] < RESEND_STOP_INTERVAL:
			return
		w.remote_senders[local][remote] = (w.remote_senders[local][remote][0], time.time())
		#:TODO: dumb code: set doesn't support indexing
		#sender_ip,sender_asid = w.remote_senders[local][SENDER][0]
		sender_ip,sender_asid = list(w.remote_senders[local][SENDER])[0]

		#:REFINE: need senders field in pkt?
		#send_pkt = Message(
		#		type=MessageType.STOP,
		#		hash=h,
		#		sender_ip=sender_ip,
		#		sender_asid=sender_asid,
		#		src_ip=local_ip,
		#		src_asid=local_asid,
		#		dst_addrs={remote_ip:remote_asid},
		#		timestamp=time.time()
		#)
		stop_pkt = self.stop_pkt
		stop_pkt.file_hash = h
		stop_pkt.sender_addr = message.IPStringtoByte(sender_ip)
		stop_pkt.sender_asid = sender_asid
		stop_pkt.src_asid = local_asid
		stop_pkt.dst_addr[0] = message.IPStringtoByte(remote_ip)
		stop_pkt.dst_asid[0] = remote_asid
		stop_pkt.dst_num = chr(1)
		stop_pkt.timestamp = time.time()
		self.sock.sendto(self.stop_msg.dumps(),(remote_ip,EXTERNAL_PORT))


	def regular_clean_connection(self):
		while True:
			#cant iterate directly because w.remove_expired_connection may modify the dict
			temp_list = []
			for w in modules.worker_pool.finished_worker.itervalues():
				temp_list.append(w)
			if temp_list:
				printf("finished len=%d"%(len(temp_list),), "WARNING", YELLOW)
			for w in temp_list:
				w.remove_expired_connection()
			#gevent.sleep(REAL_STOP_INTERVAL)

