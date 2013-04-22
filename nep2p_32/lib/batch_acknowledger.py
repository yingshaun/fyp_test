from util.singleton import Singleton
import threading
import time
from util.message import *
from util.config import *
import modules

@Singleton
class batch_acknowledger(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._ack = {} #{(src,dst):[]}
		self.lock = threading.Lock()
		self.interval = conf['batchack_interval'] if 'batchack_interval' in conf else 0.1
	
	def run(self):
		myip = modules.ip.myip

		while True:
			self.lock.acquire()

			if len(self._ack) > 0:
				for (src, dst), ll in self._ack.iteritems():
					send_pkt = Message(
							type=MessageType.ACK,
							src_ip=myip,
							src_asid=src,
							dst_addrs={dst[0]:dst[1]},
					)
					while len(ll):
						ll_send = ll[:55]
						ll = ll[55:]
						send_pkt.payload = ','.join([`n` for n in ll_send])
						modules.external_gateway.sock.sendto(send_pkt.encode(), (dst[0],EXTERNAL_PORT))
				self._ack.clear()

			self.lock.release()
			time.sleep(self.interval)

	def add(self, src, dst, timestamp):
		self.lock.acquire()

		if (src, dst) in self._ack:
			#self._ack[src, dst].append(time.time() - timestamp)
			self._ack[src, dst].append(timestamp)
		else:
			#self._ack[src, dst] = [time.time() - timestamp]
			self._ack[src, dst] = [timestamp]

		self.lock.release()
