#import logging
import random, time
from util.common import *
from util.config import *
#from util.internal_message import *
from util.message import *
from util.node_list import NodeList
from util.singleton import Singleton
from util.logger import *
import gateway
import modules

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

		#############################################################################
		self.myLogger = Logger('log/recv_' + str(time.time()))
		self.myLogger.logline('# Start of logging: ' + time.ctime())
		self.myCount = dict()			#{(ip, asid): (timestamp, count)}
		#self.myCount = (0, (u'0',0), 0)	# (timestamp, (ip, asid), count)
		#############################################################################


	#####################################################################################
	def __del__(self):
		#self.myLogger.logline(str(self.myCount))i
		for tmp_remote in self.myCount.keys():
			myCurCount = self.myCount[tmp_remote]
			self.myLogger.logline('{0}; {1}; {2}'.format(tmp_remote, myCurCount[0], myCurCount[1]))
		self.myLogger.logline('# End of logging: ' + time.ctime())
		self.myLogger.close()
	#####################################################################################

	def process_pkt(self, pkt):
		if self.NO_PROCESS:
			return
		st = time.time()
		#self.sock_count += 1

		#process the packets
		t = time.time()
		#check validity of message
		if not MessageType.isValid(pkt['type']):
			return
		#pkt = Message.decode_dict(pkt)
		self.msg_decode_time += time.time()-t
		#print 'pkt', pkt

		#node list keep alive
		self.node_list.updateRecvTime(pkt['src_ip'])

		try:
			local = pkt['dst_addrs'][self.myip]
		except KeyError:
			local = 0
			if 'dst_addrs' in pkt:
				printf("Can't find self %s in dst_addrs(%s)"%(self.myip,pkt['dst_addrs']), 'process local', YELLOW)
			else:
				printf("%s"%(pkt,), "process local", YELLOW)
		remote = (pkt['src_ip'], pkt['src_asid'])
		w = modules.worker_pool.get_worker(pkt['hash']) if 'hash' in pkt else None
		send_to_me = True if (self.myip in pkt['dst_addrs'] and modules.bidict.asid_exist(pkt['dst_addrs'][self.myip])) else False
		#printf("send_to_me=%d pkt_type=%d PKT=%d"%(send_to_me,pkt['type'],MessageType.PACKET), "recv", BLUE)

		if pkt['type'] == MessageType.PACKET:
			if send_to_me == True:

				#########################################################################
				#self.myLogger.logline(str(pkt))
				#self.myLogger.logline('{0}, {1}, {2}'.format(time.time(), remote, len(str(pkt))))	
				tmp_remote = remote
				#curTime = float('%0.1f'%time.time())	# Precision: 0.01 seconds
				curTime = int(time.time())	# Precision: 1 seconds
				
				myCurCount = self.myCount.get(tmp_remote)
                                if myCurCount == None:
                                        self.myCount[tmp_remote] = (curTime, 1)
                                elif curTime == myCurCount[0]:
                                        self.myCount[tmp_remote] = (curTime, myCurCount[1] + 1)
                                else:
                                        self.myLogger.logline('{0}; {1}; {2}'.format(tmp_remote, myCurCount[0], myCurCount[1]))
					self.myCount[tmp_remote] = (curTime, 1)
 
				'''
				if curTime == self.myCount[0] and str(remote) == str(self.myCount[1]):
					self.myCount = (self.myCount[0], self.myCount[1], self.myCount[2] + 1)
					#print self.myCount
				else:
					self.myLogger.logline(str(self.myCount))
					self.myCount = (curTime, remote, 1)
				'''
				########################################################################
				


				#get the worker and init its decoder (similar to that in IGW)
				w.init_decoder(pkt['size'])
				if local not in w.remote_senders:
					w.remote_senders[local] = {}
					#:REFINE: complete real sender part
					w.remote_senders[local][(0, 0)] = set()
					w.remote_senders[local][(0, 0)].add((pkt['sender_ip'],pkt['sender_asid']))

				#update the keep alive time of this connection
				c = modules.connection_pool.get_connection(local, remote)
				c.down_worker.add(w)
				if remote not in w.remote_senders[local]:
					w.remote_senders[local][remote] = (0, 0)
				w.remote_senders[local][remote] = (time.time(), w.remote_senders[local][remote][1])

				#append a new packet for sending ack
				t = time.time()
				modules.batch_acknowledger.add(local, remote, pkt['timestamp'])
				self.ack_time += time.time()-t

				#print 'pkt', pkt
				#do different things with different status
				#if WAITING_FIN, remote side may lost the stop message, so send it again
				if w.decode_status == INITIALIZED:
					w.decode_status = DECODING
				if w.decode_status == DECODING:
					#printf('payload length=%d'%(len(pkt.payload)),'PACKET', GREEN)
					t = time.time()
					if not self.STOP_DECODER:
						w.receive_pkt(pkt.payload)
					self.decode_time += time.time()-t
					#if random.randint(1, 800) == 1:
					#	printf('num_sent=%d num_received=%d time=%f'%(w.num_sent,w.num_received, time.time()),'PACKET', GREEN)
					c.num_received += 1
				elif w.decode_status == WAITING_FIN:
					self.send_stop_message(w, local, remote)

				t = time.time()
				#:TODO:
				#connection_pool.to_helper(pkt)
				#:REFINE: maybe done in helper?
				#send the pkt to others
				if pkt['sender_ip'] == pkt['src_ip'] and \
						pkt['sender_asid'] == pkt['src_asid'] and \
						pkt['src_ip'] != self.myip:
					pkt['src_ip'] = self.myip
					pkt['src_asid'] = local
					pkt['timestamp'] = time.time()
					for ip,asid in pkt['dst_addrs'].iteritems():
						if ip == self.myip:
							continue
						cc = modules.connection_pool.get_connection(local, (ip,asid))
						if local not in w.local_senders:
							w.local_senders[local] = set()
						if w not in cc.up_worker:
							cc.add_up_worker(w)
						w.local_senders[local].add((ip,asid))
						try:
							cc.add_pkt(pkt)
						except Exception, e:
							#logging.exception("add_pkt!?")
							pass
						if not modules.scheduler.connection_scheduled(cc):
							print 'schedule', local, (ip,asid)
							modules.scheduler.schedule_connection(cc)
						if self.FLOOD:
							print 'no add_pkt done'
						#self.sock.sendto(pkt.encode(), (ip,EXTERNAL_PORT))
						#:TODO: add back the app_worker.num_sent
						#w.num_sent += 1
						#c.num_sent += 1
				self.ttt += time.time()-t
			#else give it to helper
			#else:
			#	pass

		elif pkt['type'] == MessageType.ACK:
			#printf('%s %s'%(local,remote),"ACK", RED)
			c = modules.connection_pool.get_connection(local, remote)
			if self.DEBUG:
				printf(pkt.payload, "ACK", RED)
			try:
				c.on_acknowledgement(pkt.payload.split(','))
			except Exception, e:
				#logging.exception("on_ack failed")
				pass

		elif pkt['type'] == MessageType.STOP:
			if send_to_me == True:
				printf("STOP received: %s %s"%(local,remote), "WARNING", YELLOW)
				w.stop_sending_to_remote(local, remote)

			#TODO: how about helper
			#give the packet to worker pool and helper
			#self.worker_pool.give_pkt_to_helper(pkt)

		elif pkt['type'] == MessageType.STATUS or pkt['type'] == MessageType.KEEPALIVE:
			#:REFINE: update node list
			self.node_list.updateRecvTime(pkt['src_ip'])

		self.sock_time += time.time()-st

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
		send_pkt = Message(
				type=MessageType.STOP,
				hash=h,
				sender_ip=sender_ip,
				sender_asid=sender_asid,
				src_ip=local_ip,
				src_asid=local_asid,
				dst_addrs={remote_ip:remote_asid},
				timestamp=time.time()
		)
		self.sock.sendto(send_pkt.encode(),(remote_ip,EXTERNAL_PORT))


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

