import json
import random, os
from util.common import hashFile, hashFunc
from util.config import *
from util.internal_message import *
from util.singleton import Singleton
import gateway
import modules

@Singleton
class internal_gateway(gateway.gateway):
	def __init__(self):
		gateway.gateway.__init__(self)
		self.ip = '0.0.0.0'
		self.port = INTERNAL_PORT

	def process_pkt(self, pkt):
		#new client connects to IGW, register its src port
		if not modules.bidict.port_exist(pkt['src_port']):
			if pkt['type'] == InternalMessageType.HI:
				modules.bidict.register_port(pkt['src_port'])

		#existing client sends command to IGW
		else:
			#prepare the return packet
			ret_pkt = {}
			ret_pkt['type'] = InternalMessageType.RETURN

			#if command is binding an asid
			if pkt['type'] == InternalMessageType.BIND:
				print 'src_port:%d asid:%d'%(pkt['src_port'], pkt['asid'])
				ret_pkt['val'] = modules.bidict.link_port_asid(pkt['src_port'], pkt['asid'])
			
			#if command is sending something
			elif pkt['type'] == InternalMessageType.SEND_HEAD:
				#help client bind an asid if do not bind before
				random_start = random.randint(1, 65535)
				next_num = random_start
				while modules.bidict.get_asid_from_port(pkt['src_port']) == 0:
					modules.bidict.link_port_asid(pkt['src_port'], next_num)
					next_num = 1 if next_num == 65535 else next_num + 1
					if next_num == random_start:
						ret_pkt['val'] = -1
						self.sock.sendto(json.dumps(ret_pkt), ('127.0.0.1', pkt['src_port']))	# shaun
						return

				#read the file content if input is a file
				if pkt['send_type'] == InternalMessageType.SEND_FILE:
					#pkt['content'] = open(pkt['filepath']).read()
					pass
				
				ret_pkt['val'] = os.path.getsize(pkt['filepath'])

				#get necessary info to create connection and worker
				asid = modules.bidict.get_asid_from_port(pkt['src_port'])
				local = asid #no need to know my ip
				h = hashFile(pkt['filepath'])

				#get the corresponding worker and init its encoder
				w = modules.worker_pool.get_worker(h)
				w.init_encoder(pkt['filepath'])
				if local not in w.local_senders:
					w.local_senders[local] = set()
				
				#get each connection (create it if does not exist)
				#and link connection, worker together by hash
				#finally enqueue the connection to egw's scheduler
				for remote_ip, remote_asid in pkt['dst_addrs'].iteritems():
					remote = (remote_ip, remote_asid)
					c = modules.connection_pool.get_connection(local, remote)
					c.add_up_worker(w)
					w.local_senders[local].add(remote)
					modules.scheduler.schedule_connection(c)

			#if command is closing the socket
			#close socket: remove all connection linked to the asid while keeping worker
			elif pkt['type'] == InternalMessageType.BYE:
				local = modules.bidict.get_asid_from_port(pkt['src_port'])
				ret_pkt['val'] = modules.bidict.unlink_port(pkt['src_port'])

				temp = []
				for addr_info, c in modules.connection_pool.connection.iteritems():
					local_asid = addr_info[0]
					remote = addr_info[1]
					if local_asid == local:
						#delete sending workers, stop_sending_to_remote will modify up_worker
						temp_list1 = []
						for w in c.up_worker:
							temp_list1.append(w)
						for w in temp_list1:
							w.stop_sending_to_remote(local, remote)
	
						#delete receiving workers, stop_receiving_from_remote will modify down_worker
						temp_list2 = []
						for w in c.down_worker:
							temp_list2.append(w)
						for w in temp_list2:
							w.stop_receiving_from_remote(local, remote)
	
						#delete connection in scheduler
						modules.scheduler.unschedule_connection(c)
	
						#append this connection to list to be removed later
						temp.append(addr_info)
				for addr_info in temp:
					del modules.connection_pool.connection[addr_info]

			#finally send back the return packet
			self.sock.sendto(json.dumps(ret_pkt), ('127.0.0.1', pkt['src_port']))	#shaun

