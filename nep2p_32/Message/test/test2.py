import ctypes
import time
from message import *

if __name__ == "__main__":
	m = message.create_message(2)
	print m.filehash
	m.set_fileinfo(30000, 'hehlllo')
	print m.filehash
	print m.filesize
	m.file_size = 30000
	m.dst = [
		('192.168.84.208', 30011),
		('192.168.084.08', 1)
		]
	print m.dst

	#convert to python str
	print '=============== convert to python str   ==============='
	str_m = message.dumps(m)
	print 'ord', type(str_m), [ord(c) for c in str_m[:100]]
	print 'str', type(str_m), [c for c in str_m[:100] if c>='a' and c<='z']
	t = time.time()
	for i in xrange(10000):
		message.dumps(m)
	print 'time:', time.time()-t

	#convert to message structure
	print '=============== convert to message struct   ==============='
	m2 = message.loads(str_m)
	str_m = message.dumps(m2)
	print 'ord', type(str_m), [ord(c) for c in str_m[:100]]
	print 'str', type(str_m), [c for c in str_m if c>='a' and c<='z']
	print m2.filehash
	m2.set_fileinfo(30000, 'hehlllo')
	print m2.filehash
	print m2.filesize
	m2.file_size = 30000

	print '=============== rest  ==============='
	#message.destroy_message(m)
	m = None
	print 'set None'
	m = message.create_message(3)
	print 'created new'
	print m
	m = None
	print 'set None again'

	message.destroy_message(m)
