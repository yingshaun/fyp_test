from ctypes import *
import ctypes

import os, sys, socket

__all__ = ['message']

platform = sys.platform
if "darwin" == platform:
	lib = cdll.LoadLibrary("libmessage.dylib") 
elif platform.startswith("linux"):
	lib = cdll.LoadLibrary("libmessage.so") 

#:TODO: will be the exact message size
MAX_PAYLOAD = 1056

#IPv4 only
class message(ctypes.Structure):
	_pack_ = 1
	_fields_ = [("msg_type", c_ubyte),
			("payload_len", c_short),
			("sender_addr", c_ubyte*6),
			("src_addr", c_ubyte*6),
			("dst_num", c_ubyte),
			("dst_addr", c_ubyte*60),
			("file_size", c_int),
			("file_hash", c_char*32),
			("payload", c_ubyte*MAX_PAYLOAD),
	]

	@property
	def sender(self):
		ip,port = cast(ctypes.addressof(self.sender_addr),POINTER(c_ubyte)), cast(ctypes.addressof(self.sender_addr)+4, POINTER(c_ushort))
		ret_ip = (c_char*15)()
		lib.ip_byte_to_string(ip, ret_ip)
		return ret_ip.value, socket.ntohs(port.contents.value)
	@sender.setter
	def sender(self, addr):
		lib.set_sender(cast(ctypes.addressof(self), POINTER(message)), c_char_p(addr[0]), addr[1])

	@property
	def src(self):
		ip,port = self.src_addr, cast(ctypes.addressof(self.src_addr)+4, POINTER(c_ushort))
		ret_ip = (c_char*15)()
		lib.ip_byte_to_string(ip, ret_ip)
		return ret_ip.value, socket.ntohs(port.contents.value)
	@src.setter
	def src(self, addr):
		lib.set_src(cast(ctypes.addressof(self),POINTER(message)), c_char_p(addr[0]), addr[1])

	@property
	def dst(self):
		addrs = []
		ret_ip = (c_char*15)()
		for i in xrange(int(self.dst_num)):
			ip,port = cast(ctypes.addressof(self.dst_addr)+6*i,POINTER(c_ubyte)), cast(ctypes.addressof(self.dst_addr)+4+6*i, POINTER(c_ushort))
			lib.ip_byte_to_string(ip, ret_ip)
			addrs.append((ret_ip.value, socket.ntohs(port.contents.value)))
		return addrs
	@dst.setter
	def dst(self, addrs):
		for addr in addrs:
			lib.set_dst(cast(ctypes.addressof(self),POINTER(message)), c_char_p(addr[0]), addr[1])
			self.dst_num += 1

	def clear_dst(self):
		#lib.clear_dst(cast(ctypes.addressof(self),POINTER(message)))
		self.dst_num = 0
	def set_fileinfo(self, size, hash):
		lib.set_fileinfo(cast(ctypes.addressof(self),POINTER(message)), size, c_char_p(hash))
	def set_payload(self, payload):
		lib.set_payload(cast(ctypes.addressof(self),POINTER(message)), c_char_p(payload))

	@property
	def data(self):
		return ctypes.string_at(self.payload, ctypes.sizeof(self.payload))[:self.data_len]
	@data.setter
	def data(self, payload):
		self.data_len = len(payload)
		lib.set_payload(cast(ctypes.addressof(self),POINTER(message)), c_char_p(payload))
	@property
	def data_len(self):
		return socket.ntohs(self.payload_len)
	@data_len.setter
	def data_len(self, data_len):
		self.payload_len = socket.htons(data_len)

	@property
	def filesize(self):
		return socket.ntohl(self.file_size)

	@property
	def filehash(self):
		#return cast(self.file_hash, c_char_p).value
		return self.file_hash

	@classmethod
	def create_message(cls, msg_type=2, payload_size=MAX_PAYLOAD):
		tm = lib.create_message(c_int(msg_type), c_int(payload_size))
		#s = ctypes.create_string_buffer(ctypes.sizeof(cls))
		#print 'sizeof(contents):%d sizeof(tm):%d sizeof(cls):%d'%(ctypes.sizeof(tm.contents), ctypes.sizeof(tm), ctypes.sizeof(cls))
		s = ctypes.string_at(tm, ctypes.sizeof(cls))
		m = ctypes.cast(s, POINTER(cls)).contents
		m._s = s
		lib.destroy_message(tm)
		return m

	@classmethod
	def destroy_message(cls, msg):
		#lib.destroy_message(msg)
		pass

	def clone(self):
		return message.loads(message.dumps(self))

	@classmethod
	def dumps(cls, msg):
		#return ctypes.string_at(ctypes.addressof(msg), ctypes.sizeof(cls))
		return msg._s

	@classmethod
	def loads(cls, msg_str):
		s = ctypes.create_string_buffer(len(msg_str))
		s.raw = msg_str
		m = ctypes.cast(s, ctypes.POINTER(message)).contents
		m._s = s
		return m

	def __del__(self):
		#print 'del message:',self
		#lib.destroy_message(cast(ctypes.addressof(self),POINTER(message)))
		pass

lib.create_message.restype = POINTER(message)

if __name__ == "__main__":
	msg = lib.create_message(c_int(2), c_int(MAX_PAYLOAD))
	msg.contents.sender = '192.102.84.208', 258
	#print [int(c) for c in msg.contents.sender_addr]
	print 'sender', msg.contents.sender
	msg.contents.src = '192.102.84.208', 258
	print 'src', msg.contents.src
	msg.contents.set_fileinfo(10000, 'abcdeg'*100)
	print socket.ntohs(msg.contents.payload_len)
	print msg.contents.filesize, msg.contents.filehash
	msg.contents.dst = [
			('192.102.84.208', 2258),
			('192.112.64.178', 44258),
			('192.022.94.248', 1258),
			('192.202.34.108', 4258),
	]
	print msg.contents.dst
	msg.contents.clear_dst()
	msg.contents.set_payload('0123456789'*110)
	print len(cast(msg.contents.payload, c_char_p).value)
	#sys.exit(0)

	print 300/256 + 300%256*256
	msg = lib.create_message(c_int(2), c_int(MAX_PAYLOAD))
	print dir(msg)
	print msg, msg.contents.payload_len
	print msg.contents.dst_num
	msg.contents.dst_num = c_ubyte(100)
	print msg.contents.dst_num
	lib.clear_dst(msg)
	print msg.contents.dst_num

	a = ctypes.create_string_buffer(100)
	print dir(a)
	a.value = "192.168.84.204\00000001"
	print type(a)
	lib.set_sender(msg, a, c_ushort(3933))
	print type(msg.contents.sender_addr)
	print [int(c) for c in msg.contents.sender_addr]
	lib.set_fileinfo(msg, 65536, a)
	print [c for c in msg.contents.file_hash], msg.contents.file_size

	lib.set_payload(msg, a)
	print [chr(c) for c in msg.contents.payload[:100]]

	print sizeof(msg.contents)

	#b = ctypes.cast(ctypes.addressof(message()), POINTER(message))
	b = lib.create_message(1, MAX_PAYLOAD)
	b.contents = msg.contents #YES! can cause SEGFAULT
	print ctypes.addressof(b), ctypes.addressof(msg)
	#print type(b.contents)
	#ctypes.memmove(b, msg, 4208) #:TODO: will not cause SEGFAULT?
	#b = cast(b, POINTER(message))
	print [chr(c) for c in b.contents.payload[:100]]

	
	#seg fault! (Y) :D:D:D:D
	#lib.destroy_message(msg)
	#ctypes.memset(b, 0, 4208)

