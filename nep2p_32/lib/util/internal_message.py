import json as ujson
import base64

__all__ = ['InternalMessageType', 'InternalMessage']

class InternalMessageType:
	_maxValue = 14

	HI, \
	BYE, \
	BIND, \
	RETURN, \
	SEND_HEAD, \
	SEND_SIZE, \
	SEND, \
	SEND_FILE, \
	RECV_HEAD, \
	RECV, \
	RECV_FILE, \
	STOP, \
	RECODE_PACKETS, \
	PACKETS = range(101, _maxValue+101)

	@classmethod
	def isValid(cls, messageType):
		return messageType>=101 \
				and messageType<cls._maxValue+101

class InternalMessage(dict):
	def __init__(self, *arg, **kargs):
		dict.__init__(self)
		self.payload = ''
		for k,v in kargs.iteritems():
			self[k] = v

	def __setitem__(self, key, value):
		if key == 'type' and not InternalMessageType.isValid(value):
			raise Exception("Invalid type value %d"%value)
		elif key == 'data':
			self.payload = base64.b64decode(value)
		else:
			dict.__setitem__(self, key, value)

	def encode(self):
		p = self.copy()
		if self.payload:
			p['data'] = base64.b64encode(data)
		return ujson.dumps(p)+"\n"

	@classmethod
	def decode(cls, msg):
		return cls.decode_dict(ujson.loads(msg))
	@classmethod
	def decode_dict(cls, d):
		try:
			return cls(**d)
		except Exception, e:
			print "decodePacket exception: %s"%e
			return None


if __name__ == "__main__":
	from common import hashFunc

	m = InternalMessage(type=InternalMessageType.BIND)
	m['hehe'] = '123'
	m['haha'] = 345
	print 'm.encode:', m.encode()
	m2 = InternalMessage.decode(m.encode())
	print m2
	m2['payload'] = "hello\x00"
	print m2
	print "hash: %s"%(hashFunc(m2['payload']))
	print InternalMessage(
		type=InternalMessageType.RECV,
		hash='123',
		asid=101010
	).encode()

	p = False
	try:
		m2['type'] = 10 #Invalid type number
	except Exception:
		p = True
	if p:
		print 'Fine'
	else:
		print 'Not fine'
