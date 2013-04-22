import hashlib
from config import *

def hashFile(path):
	f = open(path)
	m = hashlib.sha256()
	while True:
		s = f.read(4096)
		if len(s) == 0:
			break
		m.update(s)
	return m.hexdigest()

def hashFunc(data):
	m = hashlib.sha256()
	m.update(data)
	return m.hexdigest()

def packetId(packet):
	''':REFINE: Needs to follow where to grab the id'''
	if len(packet)==PACKET_SIZE:
		return ord(packet[0]) + ord(packet[1])*256
	return -1

def printf(msg, mark, color=NONE):
	print '{0}[{1:^10}] {2}{3}'.format(color, mark, msg, NONE)

#def calScore(connected, numReceived, bandwidth):
#	v = ((5*(20-int(math.log(connected+1,2))))*math.log((5*(20-int(math.log(connected+1,2)))),10)+int(math.log(numReceived/BATCH_SIZE+0.1,2)**2))*math.log10(bandwidth*10+2)
#	return int(v)

if __name__ == "__main__":
	s = "hello\x00"
	print "hash: %s"%(hashFunc(s))
