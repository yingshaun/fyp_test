'''

	:TODO: need to be thread-safe here
'''
import time
from config import EXTERNAL_PORT, KEEPALIVE_TIME

__all__ = ['NodeList']

class NodeList:
	def __init__(self):
		self.ll = {} #{ip:{t_send,t_recv}}

	def _updateTime(self, node, timeType):
		if node not in self.ll:
			self.ll[node] = {
				't_send': time.time(),
				't_recv': time.time()
			}
		else:
			self.ll[node][timeType] = time.time()
		
	def updateRecvTime(self, ip):
		self._updateTime(ip, 't_recv')

	def updateSendTime(self, ip):
		self._updateTime(ip, 't_send')

	def pickNodes(self, num):
		#:REFINE: random pick
		if num>len(self.ll):
			return self.ll.copy()
		else:
			return random.sample(self.ll, num)
		pass

	def regular(self):
		kat = KEEPALIVE_TIME/3
		ret = []
		del_list = []

		for ip,s in self.ll.iteritems():
			t = time.time()
			if t-s['t_recv']>KEEPALIVE_TIME:
				del_list.append(ip)
			elif t-s['t_send']>kat:
				#self.updateSendTime(ip, m)
				ret.append(ip)
		for ip in del_list:
			del self.ll[ip]
		return ret

if __name__ == "__main__":
	n = NodeList()
	n.updateRecvTime('123')
	n.updateSendTime('123')
	n.updateSendTime('456')
	n.regular()
	print n.ll
	time.sleep(15)
	n.regular()
	print n.ll
