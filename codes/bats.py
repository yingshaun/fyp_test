# The following modules are required: ctypes, os, math, random
# from ctypes import *
# import ctypes
from cffi import FFI

import os, sys
import math
from random import *
def load_library_using_ctypes():
	platform = sys.platform
	if "darwin" == platform:
		lib = cdll.LoadLibrary("libbatscore.dylib") 

	elif platform.startswith("linux"):
		lib = cdll.LoadLibrary(os.getcwd() + '/' + "libbatscore.so") 
	return lib


# lib = load_library_using_ctypes()
# lib.bats_init.argtypes = []
# lib.bats_init()

ffi = FFI()
ffi.cdef("""

	int bats_init();

	typedef unsigned char SymbolType;


	typedef struct BatsEncoder BatsEncoder;
	BatsEncoder* BatsEncoder_new(int M, int K, int T, SymbolType *input);
    char* BatsEncoder_genPacket(BatsEncoder *encoder);
	void BatsEncoder_setDegreeDist(BatsEncoder *encoder, double *degreeDist, int maxDeg);
	void BatsEncoder_selectDegree(BatsEncoder *encoder);
	int BatsEncoder_getSmallestBid(BatsEncoder *encoder);
	
	typedef struct BatsDecoder BatsDecoder;
	BatsDecoder* BatsDecoder_new(int M, int K, int T, SymbolType *output);
    int BatsDecoder_complete(BatsDecoder* decoder, double decRatio);
    int BatsDecoder_getDecoded(BatsDecoder* decoder);
    void BatsDecoder_rankDist(BatsDecoder* decoder, double* rd);
    void BatsDecoder_receivePacket(BatsDecoder* decoder, uint8_t *batch);
	int BatsDecoder_readyForInact(BatsDecoder* decoder);
	int BatsDecoder_inactDecoding(BatsDecoder* decoder);
    void BatsDecoder_setDegreeDist(BatsDecoder* decoder, double* degreeDist, int maxDeg);
    void BatsDecoder_selectDegree(BatsDecoder* decoder);
	void BatsDecoder_logRankDist(BatsDecoder *decoder);
	int BatsDecoder_numInact(BatsDecoder *decoder);

	typedef struct NCCoder NCCoder;
	NCCoder* NCCoder_new(int batchSize, int packetSize);
    void NCCoder_genPacket(NCCoder* recoder, SymbolType *dstPacket, SymbolType *cache, int cacheSize);

	typedef struct ThreadedCircularBuf ThreadedCircularBuf;

	void bufInit(struct ThreadedCircularBuf* buf, int len, int N, char* tag);
	void bufWrite(struct ThreadedCircularBuf* buf, SymbolType* data); //Temp
	int bufRead(struct ThreadedCircularBuf* buf, SymbolType* data);
	void bufFree(struct ThreadedCircularBuf* buf);
	double bufGetFilledRatio(struct ThreadedCircularBuf* buf);

	struct ThreadArg
	{
		int M, K, T, F;
		struct ThreadedCircularBuf* buf;
		SymbolType* out;
		int* numDec; //To store the current number of decoded packets. 4, Sep, Tom.
		int* numReceived; // To store the current number of packets received for decoding. Hu Ming.
		int (*callback)(void);
	};

	void* NonBlockingDecoder_Threadfunc(void* arg);
	struct ThreadedCircularBuf* NonBlockingDecoder_new(int M, int K, int T, int F, SymbolType* output, int* numDec, int* numReceived, int (*callback)(), char* tag);
	void NonBlockingDecoder_wait(struct ThreadedCircularBuf *buf);

	""")

platform = sys.platform
if "darwin" == platform:
	lib = ffi.dlopen("libbatscore.dylib")
elif platform.startswith("linux"):
	lib = ffi.dlopen( os.getcwd() + "/libbatscore.so")


lib.bats_init()

BATCH_SIZE = 16
ORDER = 8
PACKET_SIZE = 1024


class Encoder(object):
	@classmethod
	def fromfile(cls, path):
		size = os.path.getsize(path)

		byte = open(path, 'rb').read()
		self = cls(BATCH_SIZE, int(math.ceil(size/float(PACKET_SIZE))), PACKET_SIZE, byte)
		self.s = byte
		return self

	def __init__(self, batchsize, pktnum, pktsize, file_str):
		# self.byte_string = create_string_buffer(file_str)
		# lib.BatsEncoder_new.restype = c_void_p
		# lib.BatsEncoder_new.argtypes = [c_int, c_int, c_int, POINTER(c_char)]
		# self.obj = c_void_p(lib.BatsEncoder_new(c_int(batchsize), 
		# 					c_int(pktnum), 
		# 					c_int(pktsize), 
		# 					self.byte_string))
		self.cdata = ffi.new("char[]", file_str)
		self.obj = lib.BatsEncoder_new(batchsize, pktnum, pktsize, self.cdata)

		# lib.BatsEncoder_selectDegree.argtypes = [c_void_p]
		# lib.BatsEncoder_selectDegree(self.obj)

		lib.BatsEncoder_selectDegree(self.obj)

		self.M = batchsize
		self.K = pktnum
		self.T = pktsize
		self.pkt_id_in_batch = -1

	def genPacket(self):
		#print 'Calling genPacket...'
		#emit the first stored packet in a new batch
		#	self.pkt_id_in_batch += 1
		#	#print 'pkt_id_in_batch: ', self.pkt_id_in_batch
		#	if self.pkt_id_in_batch == self.M:
		#		self.pkt_id_in_batch = -1
		#		return ''
		
		# lib.BatsEncoder_genPacket.restype = c_void_p
		# lib.BatsEncoder_genPacket.argtypes = [c_void_p]
		# result = lib.BatsEncoder_genPacket(self.obj)
		# send = ctypes.string_at(result, 2+self.M+self.T)
		result = lib.BatsEncoder_genPacket(self.obj)
		buffer = ffi.buffer(result, 2+self.M+self.T)
		return buffer[:]
		

class Decoder(object):
	@classmethod
	def tofile(cls, path, size):
		self = cls(BATCH_SIZE, int(math.ceil(size/float(PACKET_SIZE))), PACKET_SIZE)
		self.filepath = path
		self.filesize = size
		return self
	def __init__(self, batchsize, pktnum, pktsize):

		self.M = batchsize
		self.K = pktnum
		self.T = pktsize
		# self.buf = create_string_buffer(self.K * self.T)

		# lib.BatsDecoder_new.restype = c_void_p
		# lib.BatsDecoder_new.argtypes = [c_int, c_int, c_int, POINTER(c_char)]
		# self.obj = c_void_p(lib.BatsDecoder_new(c_int(batchsize), 
		# 					c_int(pktnum), 
		# 					c_int(pktsize), 
		# 					self.buf))
		self.buf = ffi.new("char[]", self.K*self.T)
		self.obj = lib.BatsDecoder_new(batchsize, pktnum, pktsize, self.buf)
		
		# lib.BatsDecoder_selectDegree.argtypes = [c_void_p]
		# lib.BatsDecoder_selectDegree(self.obj)
		
		lib.BatsDecoder_selectDegree(self.obj)

	def receivePacket(self, recv):
		# lib.BatsDecoder_receivePacket.argtypes = [c_void_p, POINTER(c_ubyte)]
		# lib.BatsDecoder_receivePacket(self.obj, cast(c_char_p(recv), POINTER(c_ubyte)))
		lib.BatsDecoder_receivePacket(self.obj, recv)
		# new section
		if self.complete():
			if hasattr(self, 'filepath'):
				#Bugfix: remove zero pad by internal attribute filesize
				f = open(self.filepath, 'wb')
				# f.write(self.buf[:self.filesize])
				ffi_buf = ffi.buffer(self.buf, self.filesize)
				f.write(ffi_buf[:self.filesize])
				lib.BatsDecoder_logRankDist(self.obj)
			else:
				lib.BatsDecoder_logRankDist(self.obj)
				self.num_inact = lib.BatsDecoder_numInact(self.obj)


	def complete(self):
		# lib.BatsDecoder_complete.restype = c_bool
		# lib.BatsDecoder_complete.argtypes = [c_void_p, c_double]
		# return lib.BatsDecoder_complete(self.obj, c_double(1.0))
		return lib.BatsDecoder_complete(self.obj, 1.0)

	def getDecoded(self):
		return lib.BatsDecoder_getDecoded(self.obj)

	def logRankDist(self):
		lib.BatsDecoder_logRankDist(self.obj)

class Recoder(object):
	def __init__(self, batchsize=BATCH_SIZE, pktsize=PACKET_SIZE):
		self.M = batchsize
		self.T = pktsize
		# lib.NCCoder_new.restype = c_void_p
		# lib.NCCoder_new.argtypes = [c_int, c_int]
		# self.obj = c_void_p(lib.NCCoder_new(c_int(batchsize), c_int(pktsize)))
		self.obj = lib.NCCoder_new(batchsize, pktsize)

		l = pktsize + ((batchsize * ORDER) >> 3) + 2
		# self.buf = create_string_buffer(l)
		self.buf = ffi.new("char []", l)
		
	def genPacket(self, cache, cachesize):
		# lib.NCCoder_genPacket.restype = c_void_p
		# lib.NCCoder_genPacket.argtypes = [c_void_p, POINTER(c_char), POINTER(c_ubyte), c_int]
		# lib.NCCoder_genPacket(self.obj, 
		# 					  self.buf, 
		# 					  cast(c_char_p(cache), POINTER(c_ubyte)), 
		# 					  c_int(cachesize))
		# print 'Recoder: genPacket: len: ', len(self.buf.raw)
		# return self.buf.raw
		lib.NCCoder_genPacket(self.obj, self.buf, ffi.new("char []", cache), cachesize)
		buf = ffi.buffer(self.buf,  2+self.M+self.T)
		return buf[:]

def test_callback():
	print('test callback ok')
	# sys.exit(0)
	return 0

import threading
class NIOWaiter(threading.Thread):
	def __init__(self, decoder, callback):
		threading.Thread.__init__(self)
		self.decoder = decoder
		self.callback = callback

	def run(self):
		self.decoder.waitDecodingThread()
		# print 'python waite complete'
		self.decoder.done = True

		self.decoder.done = True

		f = open(self.decoder.filepath, 'w+')
		buf = ffi.buffer(self.decoder.buf, self.decoder.filesize)
		f.write(buf[:self.decoder.filesize])

		# lib.bufFree(cast(self.obj, POINTER(c_ubyte)))
		lib.bufFree(self.decoder.obj)

		self.decoder.finish = True

		self.callback()


class NIODecoder(object):
	@classmethod
	def tofile(cls, path, size, complete_callback, hash):
		self = cls(16, int(math.ceil(size/float(1024))), 1024, 8, complete_callback, hash[-8:])
		self.filepath = path
		self.filesize = size
		return self
	def __init__(self, batchsize, pktnum, pktsize, ff, user_callback, tag):
		self.done = False
		self.finish = False
		self.M = batchsize
		self.K = pktnum
		self.T = pktsize
		self.F = ff
		
		# self.buf = create_string_buffer(self.K * self.T)
		# self.numDec = c_int(0)
		# self.numReceived = c_int(0)
		# self.complete_callback = complete_callback
		# lib.NonBlockingDecoder_new.restype = c_void_p
		# MYFUNC = CFUNCTYPE(c_int)
		# def NIODecoderCallback():
		# 	print('Python callback')
		# 	# NIODecoder.onComplete(self)
		# 	self.done = True
		# 	# buf = ctypes.string_at(self.buf, self.filesize)
		# 	# open(self.filepath, 'w+').write(buf)
		# 	open(self.filepath, 'w+').write(self.buf[:self.filesize])

		# 	lib.bufFree(cast(self.obj, POINTER(c_ubyte)))
			
		# 	self.finish = True

		# 	#  user registered callback function
		# 	self.complete_callback()
		# 	return 0

		# self.callback = MYFUNC(test_callback)
		# lib.NonBlockingDecoder_new.restype = c_void_p
		# self.obj = c_void_p(lib.NonBlockingDecoder_new(c_int(batchsize), 
		# 									c_int(pktnum), 
		# 									c_int(pktsize),
		# 									c_int(ff), 
		# 									self.buf, 
		# 									byref(self.numDec), 
		# 									byref(self.numReceived), 
		# 									self.callback, 
		# 									tag))
		

		self.buf = ffi.new("char []", self.K *self.T)
		self.numDec = ffi.new("int *")
		self.numReceived = ffi.new("int *")
		self.user_callback = user_callback
		self.callback = ffi.callback("int()", test_callback)

		self.obj = lib.NonBlockingDecoder_new(batchsize, 
											pktnum, 
											pktsize, 
											ff, 
											self.buf, 
											self.numDec, 
											self.numReceived, 
											self.callback, 
											ffi.new("char []", tag))

		NIOWaiter(self, user_callback).start()

	def NIODecoderCallback():
			print('Python callback')
			# NIODecoder.onComplete(self)
			self.done = True
			# buf = ctypes.string_at(self.buf, self.filesize)
			# open(self.filepath, 'w+').write(buf)
			f = open(self.filepath, 'w+')
			buf = ffi.buffer(self.buf, self.filesize)
			f.write(buf[:self.filesize])

			# lib.bufFree(cast(self.obj, POINTER(c_ubyte)))
			lib.bufFree(self.obj)

			self.finish = True

			#  user registered callback function
			self.user_callback()

		


	def receivePacket(self, recv):
		if not self.done:
			#lib.bufWrite(self.obj, cast(c_char_p(recv), POINTER(c_ubyte)))
			#lib.bufWrite(self.obj, ffi.new("char []", recv))
			lib.bufWrite(self.obj, recv)

	def waitDecodingThread(self):
		lib.NonBlockingDecoder_wait(self.obj)

	 # do not use 'self.done' flag.
	 # Because onComplete will write file to disk, the time for it to complete is huge.
	def complete(self):
		return self.done

	def getDecoded(self):
		# return self.numDec.value
		return self.numDec[0]
	
	def getReceived(self):
		# return self.numReceived.value
		return self.numReceived[0]

	def getBufferFillRatio(self):
		# lib.bufGetFilledRatio.restype = c_double
		return lib.bufGetFilledRatio(self.obj)



if __name__ == "__main__":
	import sys
	#M = BATCH_SIZE
	#K = 512
	#T = 4
	#ff = 8
	
	#test = []
	
	#for i in range(0, K):
	#	for j in range(0, T):
	#		test.append(chr((i+1)%64 + (j%4)*64))
	
	#print test
	
	#enc = Encoder(M, K, T, ff)
	#dec = Decoder(M, K, T, ff)
	
	#enc.setInputPackets(test)
	
	#for i in range(0, M):
	#	send = enc.genPacket()
	#	print send
	
	# Create encoder instance given source filename.
	enc2 = Encoder.fromfile(sys.argv[2])
	enc = Encoder.fromfile(sys.argv[1])

	import hashlib

	def cal_hash(f, block_size):
		while True:
			data = f.read(block_size)
			if not data:
				break
			hashlib.sha256().update(data)
		return hashlib.sha256().hexdigest()
	
	myfile2 = open(sys.argv[2], 'rb')
	myfile = open(sys.argv[1], 'rb')

	# Create decoder instance given destination filename and filesize.
	def a():
		print 'a()'
	dec2 = NIODecoder.tofile('output2', os.path.getsize(sys.argv[2]), a, cal_hash(myfile2, 512*1024))
	dec = NIODecoder.tofile('output', os.path.getsize(sys.argv[1]), a, cal_hash(myfile, 512*1024))
	#NIODecoder.onComplete(self)

	myfile2.close()
	myfile.close()
	
	# Create recoder instance
	print "python-create: packetSize = %d" % PACKET_SIZE
	rec2 = Recoder(BATCH_SIZE, PACKET_SIZE)
	rec = Recoder(BATCH_SIZE, PACKET_SIZE)
	
	Rcnt = 1
	Scnt = 1

	# channel loss rate
	r = 0.05
	
	#for i in range(30000):
	#	send = enc.genPacket()
	#print "Ended"
	#sys.exit(1)
	
	# Check whether decoding is complete. (Note: no callback feature at this moment yet)
	import time
	t0 = time.time()
	#for i in range(PACKET_SIZE0):
	#	enc.genPacket()
	#print "Ended...", time.time()-t0
	#sys.exit(1)
	buf = []
	while not dec.complete() or not dec2.complete():
		send = enc2.genPacket()
		if send:
			dec2.receivePacket(send)

		send = enc.genPacket() # Generate a packet
		#Test for new batch
		if send == '':
			print "New Batch!"
			# Recode
			if len(buf) > 0:
				tmp = ''.join(buf)
				for i in range(0, BATCH_SIZE):
					if random() >= r:
						resend = rec.genPacket(tmp, len(buf))
						dec.receivePacket(resend)
						Rcnt += 1
					else:
						print "Packet lost in second link"
				# reset buffer
				del buf[0:len(buf)]
			else:
				print "All packets in batch lost"
			continue
		#simulate channel
		if random() >= r:
			buf.append(send)
		else:
			print "Packet lost in first link"
		#print send
		#print len(send)
		#dec.receivePacket(send) # Receive a packet
		#print "Dec::" + str(cnt) + "/" + str(dec.getDecoded()) + ", recv'd/dec'd, BatchID = " + str(ord(send[0])+256*ord(send[1]))
		Scnt += 1
		print 'Fill ratio', dec.getBufferFillRatio()
	print "Dec::" + str(Scnt) + "/" + str(Rcnt) + "/" + str(dec.getDecoded()) + ", sent/recv'd/dec'd"
	print "Ended...", time.time()-t0
	
	#result = [chr(x) for x in dec.buf]
	
	#print result
	
	#if test == result:
	#	print "Success!"
	#else:
	#	print "Error!"
	#	l = min(len(test), len(result))
	#	for i in range(0, l):
	#		if test[i] == result[i]:
	#			print str(i) + "-th byte same"
	#		else:
	#			print str(i) + "-th byte different: " + str(ord(test[i])) + " VS " + str(ord(result[i]))
	#	print "Length of test: " + str(len(test)) + ", Length of result: " + str(len(result))

