#
# :TODO: skipped the endian problem
#
#
from util.singleton import Singleton
import threading
import time
from util.message import MessageType
from util.bmessage import *
from util.config import *
import modules
import cffi
import collections
import gevent
from util.logger import *	# shaun

__all__ = ['batch_acknowledger']

ffi = cffi.FFI()
BASE_DELAYS_ROLLOVER = conf['congestion_rollover'] if 'congestion_rollover' in conf else 1 #seconds

# return: rollover
def update_base_delays(delay, base_delays, rollover):
	t = time.time()
	if t-rollover > BASE_DELAYS_ROLLOVER:
		base_delays.appendleft(delay)
		return t
	else:
		try:
			base_delays[0] = min(base_delays[0], delay)
		except:
			base_delays.appendleft(delay)
		return rollover

@Singleton
class batch_acknowledger(threading.Thread):
	BASE_DELAYS_LEN = conf['congestion_len'] if 'congestion_len' in conf else 10 #array length
	def __init__(self):
		threading.Thread.__init__(self)
		self._ack = {} #{(src,dst):[str,base[],[base,min,current],count,rollover]}
		self._ack_added = {}
		self.lock = threading.Lock()
		self.semaphore = threading.Semaphore(0)
		self.interval = conf['batchack_interval'] if 'batchack_interval' in conf else 0.1
		self.buffer_size = 28 #3doubles, 1int
		self.myLogger = dataFlowLogger('ack.log')	# shaun
		self.myLogger.start()				# shaun

	def __del__(self):					# shaun
		self.myLogger.stop()				# shaun
	
	def run(self):
		myip = modules.ip.myip
		msg = message(message.create_message(MessageType.ACK))
		send_pkt = msg.get_bm()
		send_pkt.src_addr = message.IPStringtoByte(myip)
		send_pkt.dst_num = chr(1)

		while 1:
			self.semaphore.acquire()
			self.lock.acquire()
			(src,dst), ll = self._ack_added.popitem()

			#send_pkt.set_src((myip,src))
			#send_pkt.clear_dst()
			#send_pkt.set_dst([dst])
			send_pkt.src_asid = src
			send_pkt.dst_addr[0] = message.IPStringtoByte(dst[0])
			send_pkt.dst_asid[0] = dst[1]

			#while len(ll):
			#	ll_send = ll[:55]
			#	ll = ll[55:]
			#	send_pkt.data = ','.join([`n` for n in ll_send])
			#send_pkt.set_payload(ffi.buffer(ll[0], self.buffer_size)[0:self.buffer_size])
			msg.set_payload(ffi.buffer(ll[0])[:])
			#modules.external_gateway.sock.sendto(bmessage.dumps(send_pkt), (dst[0],EXTERNAL_PORT))
			modules.external_gateway.sock.sendto(msg.dumps(), (dst[0],EXTERNAL_PORT))
			self.myLogger.logPkt((dst[0], dst[1]), time.time(), 1)	# shaun
			#print "run delays[%d]: %.20f %.20f %.20f"%(src,ll[2][0], ll[2][1], ll[2][2])
			ll[3][0] = 0
			self.lock.release()
			#time.sleep(self.interval)
			#gevent.sleep(self.interval)

	# timestamp == delay (check lib/gateway.py)
	def add(self, src, dst, timestamp):
		self.lock.acquire()

		#delay = time.time() - timestamp
		delay = timestamp
		if (src, dst) in self._ack:
			#self._ack[src, dst].append(time.time() - timestamp)
			#self._ack[src, dst].append(timestamp)
			a = self._ack[src, dst]
			_,base_delays,delays,count,rollover = a
			delays[1] = min(timestamp, delays[1])
			delays[2] = (delays[2]+timestamp)/2
			a[4] = update_base_delays(delay, base_delays, rollover)
			a[3][0] += 1
		else:
			#self._ack[src, dst] = [time.time() - timestamp]
			a = ffi.new("char[]", self.buffer_size) #3 doubles+1int
			b = ffi.cast("double*", a)
			c = ffi.cast("int*", a+24)
			b[0] = b[1] = b[2] = timestamp
			base_delays = collections.deque(maxlen=self.BASE_DELAYS_LEN)
			a = [a, base_delays, b, c, time.time()]
		self._ack[src,dst] = a
		if (src,dst) not in self._ack_added:
			self.semaphore.release()
		self._ack_added[src,dst] = a

		self.lock.release()

if __name__ == "__main__":
	class DumpLock():
		def __init__(self):
			self._v = True
		def acquire(self):
			assert(self._v == True)
			self._v = False
		def release(self):
			assert(self._v == False)
			self._v = True
		def __str__(self):
			return 'lock %d'%(self._v)
	class DumpSemaphore():
		def __init__(self, maxlen):
			self._v = maxlen
		def acquire(self):
			assert(self._v > 0)
			self._v -= 1
		def release(self):
			self._v += 1
		def __str__(self):
			return 'semaphore %d'%(self._v)
	bat =  batch_acknowledger.Instance()
	bat.lock = DumpLock()
	bat.semaphore = DumpSemaphore(0)

	src = 1021
	dst = ('102.212.2.2', 2012)
	#a = [1.2222,2.34141,3.41412,22.2222,1121.12111]
	a = [1.0,2.0,3.0,4.0,5.0,4.0,3.0,2.0,1.0]
	for i in a:
		bat.add(src,dst,i)
		print "add delays[%d]: %.20f %.20f %.20f %d"%(src,bat._ack[src,dst][2][0], bat._ack[src,dst][2][1], bat._ack[src,dst][2][2], bat._ack[src,dst][2][3])
		print ','.join([`ord(c)` for c in bat._ack[src,dst][0]])
	for i in a[5:]:
		bat.add(12222,dst,i)
	print bat.semaphore, bat.lock
	bat.run()
	bat.run()
	for i in a:
		bat.add(src,dst,i)
		print "add delays[%d]: %.20f %.20f %.20f %d"%(src,bat._ack[src,dst][2][0], bat._ack[src,dst][2][1], bat._ack[src,dst][2][2], bat._ack[src,dst][2][3])
		print ','.join([`ord(c)` for c in bat._ack[src,dst][0]])
