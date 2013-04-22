import socket
import ctypes
import time
from message import *

if __name__ == "__main__":
	m = message.create_message(2)
	print 'len', m.msg_type, m.payload_len
	m2 = message.create_message(2)
	print 'len', m.msg_type, m.payload_len
	m3 = message.create_message(2)

	print '=============   setting   ==============='
	#set sender
	m.sender = ('192.168.84.208', 30011)
	print 'sender', m.sender
	#set src
	m.src = ('1.1.1.1', 11)
	print 'src', m.src
	#set dst
	m.dst = [
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		]
	print 'dst', m.dst
	#str_m = message.dumps(m)
	#print 'ord', type(str_m), len(str_m), [ord(c) for c in str_m]
	#set payload
	print 'type', m.msg_type, 'payload_len', m.data_len
	#m.set_payload('0123456789abcdef'*64)
	m.data = '0123456789abcdef'*64
	print 'payload', ctypes.sizeof(m.payload), m.data_len, len(m.data), m.data
	m2 = message.loads(message.dumps(m))
	print 'payload', ctypes.sizeof(m2.payload), m2.data_len, len(m2.data), m2.data
	print 'dst', m.dst
	str_m = message.dumps(m)
	print 'ord', type(str_m), len(str_m), [ord(c) for c in str_m]

	#reset dst
	print '=============   reset   ==============='
	m.clear_dst()
	print 'dst', m.dst
	m.dst = [
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		('192.168.84.208', 30011),
		('192.168.084.08', 1),
		]
	print 'dst', m.dst

	#set fileinfo
	print 'filesize,filehash=(%s,%s)'%(type(m.filesize), type(m.filehash))
	print 'filesize,filehash=(%d,"%s")'%(m.filesize, m.filehash)
	m.set_fileinfo(30303, '192321312ffefeefeefefe')
	print 'filesize,filehash=(%d,"%s")'%(m.filesize, m.filehash)
	assert(m.filesize == 30303)
	assert(m.filehash == '192321312ffefeefeefefe')
