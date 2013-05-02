import gevent, sys
import json
from lib.util.common import hashFile, hashFunc
from lib.appsocket import AppSocket
from time import sleep

if __name__ == "__main__":
	nodes = json.loads(open("nodes.json").read())
	nodes = [(k,v) for k,v in nodes.iteritems()]
	config = json.loads(open("config.json").read())

	filepath = sys.argv[1] if len(sys.argv)>1 else ''
	if filepath:
		print 'hash:', hashFile(filepath)

	app = AppSocket()
	#gevent.sleep(6)
	print 'binding..'
	if app.bind(config['asid'])==-1:
		print 'bind failed'
		app.close()
		sys.exit(-1)

	if filepath:
		#abc = raw_input('Press enter to start sending....')
		print 'sending in 5 seconds'
		sleep(10)
		print 'sendto...'
		print app.sendfileto(nodes, filepath)
	else:
		print 'recvfrom...'
		addrs,data = app.recvfrom()
		print addrs, len(data), hashFunc(data)
	print 'preparing to close socket...'
	gevent.sleep(config['wait_close'])
	gevent.sleep(10)
	print 'closing..'
	#app.close()
	print 'closed'
