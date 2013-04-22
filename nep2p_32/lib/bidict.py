from util.singleton import Singleton

@Singleton
class bidict(object):
	def __init__(self):
		self.p2a = {}
		self.a2p = {}
	
	def register_port(self, port):
		#print 'registered:%d'%port
		return self.link_port_asid(port, 0)

	def link_port_asid(self, port, asid):
		#port must be valid
		if port < 1 or port > 65535:
			return -1

		#special case, asid not assigned (register port)
		#need to check if the port is linked before
		if asid == 0:
			if self.port_exist(port):
				return -1
			else:
				self.p2a[port] = asid
				return 0

		#asid must between 1 and 65535
		if asid < 1 or asid > 65535:
			return -1

		#if not self.port_exist(port) and not self.asid_exist(asid):
		if not self.asid_exist(asid):
			self.p2a[port] = asid
			self.a2p[asid] = port
			return 0
		else:
			return -1
	
	def link_asid_port(self, asid, port):
		return self.link_port_asid(port, asid)
	
	def port_exist(self, port):
		return port in self.p2a
	
	def asid_exist(self, asid):
		return asid in self.a2p
	
	def get_asid_from_port(self, port):
		return self.p2a[port] if self.port_exist(port) else -1
	
	def get_port_from_asid(self, asid):
		return self.a2p[asid] if self.asid_exist(asid) else -1
	
	def unlink_port(self, port):
		if self.port_exist(port):
			if self.p2a[port] != 0:
				del self.a2p[self.p2a[port]]
			del self.p2a[port]
			return 0
		else:
			return -1
	
	def unlink_asid(self, asid):
		if self.asid_exist(asid):
			del self.p2a[self.a2p[asid]]
			del self.a2p[asid]
			return 0
		else:
			return -1

if __name__ == '__main__':
	d = bidict.Instance()
	print 'register port 80:', d.register_port(80)
	print 'register port 80 again:', d.register_port(80)
	print 'link port 80 -> asid 80:', d.link_port_asid(80, 80)
	print 'link port 8080 -> asid 100:', d.link_port_asid(8080, 100)
	print 'link asid 1234 -> port 5678:', d.link_asid_port(1234, 5678)
	print 'link asid 1234 -> port 4321:', d.link_asid_port(1234, 4321)
	print 'port from asid 1234:', d.get_port_from_asid(1234)
	print 'asid from port 5678:', d.get_asid_from_port(5678)
	print 'port 1234 linked?', d.port_exist(1234)
	print 'port 5678 linked?', d.port_exist(5678)
	print 'asid 1234 linked?', d.asid_exist(1234)
	print 'asid 5678 linked?', d.asid_exist(5678)
	print 'unlink port 80', d.unlink_port(80)
	print 'unlink asid 1234', d.unlink_asid(1234)
	print 'link asid 1234 -> port 4321:', d.link_asid_port(1234, 4321)
	print 'link port 8000 -> asid 123456:', d.link_port_asid(8000, 123456)
