from cffi import FFI
import socket

__all__ = ['message']

ffi = FFI()
ffi.cdef("""
	typedef struct message_s{
	char msg_type;
	char dst_num;

	unsigned short payload_len;

	char sender_addr[4];
	char src_addr[4];

	unsigned short sender_asid;
	unsigned short src_asid;
	
	unsigned int file_size;
	char file_hash[32];

	char dst_addr[10][4];	//to be removed
	unsigned short dst_asid[10];	//to be removed

	double timestamp;
//	char payload[1042];
//  create this header once, then use .join to concat
};

""")
MAX_PAYLOAD = 1042

class message:
	HEADER_SIZE = ffi.sizeof("struct message_s")
	def __init__(self, bm):
		try:
			bm.msg_type
		except:
			bm = message.create_message()
		self._bm = bm
		self._s = ffi.cast("char*", bm)
		self._buf = ffi.buffer(self._bm)
		self._payload = ''
		self._head_buf = ''
		self.timestamp = 0.0
		
	@classmethod
	def set_dst(cls, addr):
		for addr in addrs:
			return socket.inet_aton(ip_str)

	@classmethod
	def IPStringtoByte(cls, ip_str):
		return socket.inet_aton(ip_str)

	@classmethod
	def IPBytetoString(cls, byte_str):
		return socket.inet_ntoa(ffi.buffer(byte_str)[:])
	
	def get_bm(self):
		return self._bm
		
	def set_payload(self, payload):
		self._payload = payload

	def get_payload(self):
		return self._payload

	def get_head_buf(self):
		#return ffi.buffer(self._bm)[:]
		return self._buf[:]

	def dumps(self):
		#return ffi.buffer(self._bm)[:]
		#return self._buf[:]
		return ''.join(['nem  ',self._buf[:], self._payload])
		#return ''.join(['nem  ',ffi.buffer(self._bm)[:], self._payload])

	def loads(self, msg_str):
		#return ffi.cast("struct message_s *", ffi.new("char[]", msg_str))
		self._s[0:message.HEADER_SIZE] = msg_str[:message.HEADER_SIZE]
		#print 'msg[%s]'%msg_str[message.HEADER_SIZE:message.HEADER_SIZE+17]
		#try:
		#	self.timestamp = float(msg_str[message.HEADER_SIZE:message.HEADER_SIZE+17])
		#except Exception, e:
		#	print 'failed', e
		#	print 'msg_str', [`ord(c)` for c in msg_str]
		if self._bm.msg_type == chr(7):
			#self._s[0:message.HEADER_SIZE] = msg_str[:message.HEADER_SIZE]
			self.timestamp = float(msg_str[message.HEADER_SIZE:message.HEADER_SIZE+17])
			self._payload = msg_str[message.HEADER_SIZE+17:message.HEADER_SIZE+17+self._bm.payload_len]
			#_, self.timestamp, self._payload = struct.unpack('sds', msg_str)
		else:
			self._payload = msg_str[message.HEADER_SIZE:message.HEADER_SIZE+self._bm.payload_len]
		return self

	def loads_struct(self, header, timestamp, payload):
		self._s[0:message.HEADER_SIZE] = header
		self.timestamp = timestamp
		self._payload = payload
		return self
	
	@classmethod
	def create_message(cls, msg_type=2, payload_size=MAX_PAYLOAD):
		tm = ffi.new("struct message_s *")
		tm.msg_type = chr(msg_type)
		tm.payload_len = payload_size
		return tm


if __name__ == "__main__":
	import time
	@profile
	def a():
		# msg = ffi.new("struct message_s *")
		msg = message.create_message()
		print [`ord(c)` for c in ffi.buffer(msg)]
		c = ffi.cast("char*", msg)
		print msg
		for i in range (30000):
			msg.msg_type = '2'
			msg.payload_len = 1042
			msg.sender_addr = message.IPStringtoByte("192.168.65.72")
			msg.src_addr = message.IPStringtoByte("192.168.65.73")
	
			msg.sender_asid = 258
			msg.src_asid = 260
	
			# msg.dst_addr[0] = message.IPStringtoByte("192.168.65.72")
	
			addrs = [
				('192.102.84.208', 2258),
				('192.112.64.178', 44258),
				('192.022.94.248', 1258),
				('192.202.34.108', 4258),
			]
			i = 0
			#for addr in addrs:
			#	msg.dst_addr[i] = message.IPStringtoByte(addr[0])
			#	msg.dst_asid[i] = int(addr[1])
			#	i += 1
			ip = [message.IPStringtoByte(i) for i,_ in addrs]
			port = [p for _,p in addrs]
			msg.dst_addr = ip
			msg.dst_asid = port
		mm = message(msg)
		print [`ord(c)` for c in mm._buf[:]]
		print [`ord(c)` for c in mm.dumps()]
		assert(ffi.buffer(mm._bm)[:] == mm.dumps()[5:])
	
		t = time.time()
		print time.time()
		print int(time.time() * 100000)
		msg.timestamp = t
	
		msg.file_size = 10000
		msg.file_hash = 'abc10231abcabc10231abcabc10231ab'
	
	
		
		print msg.msg_type
		print msg.payload_len
	
		print msg.sender_addr
		print message.IPBytetoString(msg.sender_addr)
	
		print msg.src_addr
		print message.IPBytetoString(msg.src_addr)
	
		print msg.sender_asid
		print msg.src_asid
	
		print msg.timestamp
		print msg.file_size
	
		print 'dst', message.IPBytetoString(msg.dst_addr[3]), msg.dst_asid[3]
	
		print ffi.buffer(msg.file_hash)[:]
	
	########## DUMP:
		#dumped = message.dumps(msg)
		dumped = mm.dumps()
		print len(dumped)
	
	######### LOAD:
		#msg2 = message.loads(dumped)
		msg2 = mm.loads(dumped[5:])._bm
		#c[0:len(dumped)] = dumped
		#msg2 = msg
	
		print msg2
		print msg2.msg_type
		print msg2.payload_len
	
		print msg2.sender_addr
		print socket.inet_ntoa(ffi.buffer(msg2.sender_addr)[:])
	
		print msg2.src_addr
		print socket.inet_ntoa(ffi.buffer(msg2.src_addr)[:])
	
		print msg2.sender_asid
		print msg2.src_asid
	
		print msg2.timestamp
		print msg2.file_size
	
		print message.IPBytetoString(msg2.dst_addr[0])
	
		print ffi.buffer(msg2.file_hash)[:]

	######## TIME:
		count = 30000
		t = time.time()
		gg1 = '1'*1176
		print type(mm.dumps())
		head_buf = mm.get_head_buf()
		for i in xrange(count):
			#len(mm.dumps())
			gg = mm.dumps()
			#gg.strip()
			#g1 = str(gg)
			#print '%s%10d%s'%(head_buf, 199, mm.get_payload())
			print gg
			print gg1
		print 'TIME', (time.time()-t)/count
	a()
