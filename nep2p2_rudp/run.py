from lib.util.config import *
import lib.modules
import logging

import threading, time, signal, sys
#import yappi
import gevent, gevent.monkey

gevent.monkey.patch_all()

def bye(signum, frame):
	print '\nBye'
	lib.modules.external_gateway.__del__()
	print 'Rcv Log File: {0}'.format(lib.modules.external_gateway.myLogger.filepath)
	lib.modules.scheduler.__del__()
	print 'Snd Log File: {0}'.format(lib.modules.scheduler.myLogger.filepath)
	sys.exit()

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	#yappi.start()

	# make all thread deamon
	lib.modules.batch_acknowledger.setDaemon(True)
	lib.modules.scheduler.setDaemon(True)
	lib.modules.external_gateway.setDaemon(True)
	lib.modules.internal_gateway.setDaemon(True)

	lib.modules.batch_acknowledger.start()
	lib.modules.scheduler.start()
	lib.modules.external_gateway.start()
	lib.modules.internal_gateway.start()
	print '1.0a16 11:55'
	
	signal.signal(signal.SIGINT, bye)
	signal.signal(signal.SIGTERM, bye)
	# while threading.active_count() > 0:
	if len(sys.argv)>1:
		gevent.sleep(float(sys.argv[1]))
	else:
		while True:
			gevent.sleep(100000000)
	#yappi.print_stats()