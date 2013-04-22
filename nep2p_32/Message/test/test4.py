import socket
import ctypes
import time
from message import *

if __name__ == "__main__":
	m = message.create_message(2, 1024)
	m.sender = '192.158.241.2', 12031
	m.src = '123.123.23.21', 32345
	m.dst = [
		('123.123.23.21', 32345),
		('123.123.23.21', 32345),
		('123.123.23.21', 32345),
		]
	print 's', len(m.dumps(m)), ','.join([c if c.isalnum() else `ord(c)` for c in m.dumps(m)])
	#m.set_payload('0123456789abcdef'*64)
	m.data = '0123456789abcdef'*64
	print 's', len(m.dumps(m)), ','.join([c if c.isalnum() else `ord(c)` for c in m.dumps(m)])

	s2 = message.dumps(m)
	m = None
	print 's2', len(s2), ','.join([c if c.isalnum() else `ord(c)` for c in s2])

	m = message.loads(s2)
	s2 = None
	print m.msg_type, m.data_len
	assert(m.msg_type==2 and m.data_len==1024)

	m2 = m.clone()
	print 'ori',
	print m.msg_type, m.data_len,
	print m2.msg_type, m2.data_len
	print 'changed m',
	m.msg_type = 1
	print m.msg_type, m.data_len,
	print m2.msg_type, m2.data_len
	print 'changed m2',
	m2.msg_type = 3
	print m.msg_type, m.data_len,
	print m2.msg_type, m2.data_len
