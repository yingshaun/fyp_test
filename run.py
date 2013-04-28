from lib.util.config import *
import lib.modules
import logging

import threading, time, signal, sys
#import yappi

def bye(signum, frame):
	print '\nBye'
	lib.modules.external_gateway.__del__()
	lib.modules.schedular.__del__()
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
	print '1.0a13 11:08'
	
	signal.signal(signal.SIGINT, bye)
	# while threading.active_count() > 0:
	if len(sys.argv)>1:
		time.sleep(float(sys.argv[1]))
	else:
		while True:
			time.sleep(100)
	#yappi.print_stats()
