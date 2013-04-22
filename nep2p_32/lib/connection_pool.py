#import gevent
from connection import connection
from util.singleton import Singleton
from util.common import conf
#from util.internal_message import *
#from util.message import *

@Singleton
class connection_pool(object):
	def __init__(self):
		self.pool = {}
		self.INIT_RATE = conf['connection_initrate'] if 'connection_initrate' in conf else 1
	
	@property
	def connection(self):
		return self.pool
	
	def get_connection(self, local, remote):
		if (local, remote) not in self.pool:
			self.pool[(local, remote)] = connection(local, remote, self.INIT_RATE) #32
		return self.pool[(local, remote)]

if __name__ == '__main__':
	c = connection_pool.Instance()
