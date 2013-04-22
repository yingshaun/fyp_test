import json as ujson
#import ujson
import base64

__all__ = ['MessageType', 'Message']

class MessageType:
	_maxValue = 7

	SYN, \
	ACK, \
	STOP, \
	DONE, \
	STATUS, \
	KEEPALIVE, \
	PACKET = range(1,_maxValue+1)
	@classmethod
	def isValid(cls, messageType):
		return messageType>=1 \
				and messageType<cls._maxValue+1

#property(srcAsaddr,dstAsaddr,senderAsaddr,hashValue,size)
#property((src_ip,src_asid),(dst_ip,dst_asid),
#		(sender_ip,sender_asid),hash,size)
class Message(dict):
	HEAD = 'nem'

	def init(self, mtype, srcAsaddr=('',0), dstAsaddr=('',0), senderAsaddr=('',0), hashValue='', size=0, payload=''):
		dict.__init__(self)
		self['type'] = mtype
		self['src_ip'],self['src_asid'] = srcAsaddr
		self['dst_ip'],self['dst_asid'] = dstAsaddr
		self['sender_ip'],self['sender_asid'] = senderAsaddr
		self['hash'] = hashValue
		self['size'] = size
		self.payload = payload

	def __init__(self, *arg, **kargs):
		dict.__init__(self)
		self.payload = ''
		for k,v in kargs.iteritems():
			self[k] = v

	def __setitem__(self, key, value):
		if key == 'type' and not MessageType.isValid(value):
			raise Exception("Invalid type value %d"%value)
		elif key == 'data':
			self.payload = base64.b64decode(value)
		else:
			dict.__setitem__(self, key, value)

	def __str__(self):
		return "%s, %i"%(dict.__str__(self), len(self.payload))

	def encode(self):
		# "%-5s%-10X%s%s"%('nem',json_len,json,payload_bin)
		# "%-5s%-10X%s%s"%('neim',json_len,json,payload_bin)
		j = ''
		if self.payload != None:
			self['length'] = len(self.payload)
			j = ujson.dumps(self)
			del self['length']
			return "%-5s%-10X%s%s"%(Message.HEAD,len(j),j,self.payload)
		else:
			j = ujson.dumps(self)
			return "%-5s%-10X%s"%(Message.HEAD,len(j),j)

	@classmethod
	def decode(cls, msg):
		if msg[:5].strip() != 'nem':
			return None
		j_len = int(msg[5:15].strip(),16)
		j = ujson.loads(msg[15:15+j_len])
		payload = None
		if 'length' in j:
			payload = msg[15+j_len:15+j_len+j['length']]
			del j['length']
		s = cls.decode_dict(j)
		s.payload = payload
		return s

	@classmethod
	def decode_dict(cls, d):
		try:
			return cls(**d)
		except Exception, e:
			print "decodePacket exception: %s"%e
			return None


if __name__ == "__main__":
	from common import hashFunc

	m = Message(
		type=3,
		hash='12333',
		src_ip='123',
		src_asid=123,
	)
	print m, m['hash']
	m.hashValue = 'abc'
	print m, m['hash']
	m['hash'] = 'ghi'
	print 'here', m, m['hash']
	m2 = Message.decode(m.encode())
	print m2
	m2.payload = "hello\x00"
	m2['src_ip'],m2['src_asid'] = ('456', 456)
	print m2
	print "hash: %s"%(hashFunc(m2.payload))
	print m2.decode(m2.encode())
	print len(Message(2).encode())
	m2['data'] = base64.b64encode('abcdefgggg')
	print m2

	p = False
	try:
		m2['type'] = 10 #Invalid type number
	except Exception:
		p = True
	if p:
		print 'Fine'
	else:
		print 'Not fine'
