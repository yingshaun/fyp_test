import os, json, time

try:
	client_config = json.loads(open('config.json', 'r').read())
except:
	client_config = {}

LOG_FILE_BASE = client_config['log_file_base'].encode() if 'log_file_base' in client_config else 'log/default/'
LOG_PRECISION = client_config['log_precision'] if 'log_precision' in client_config else 0.1


class Logger(object):
	def __init__(self, filepath, flags="w+"):
		directory = os.path.abspath(os.path.dirname(filepath))
		if not os.path.exists(directory):
			os.makedirs(directory)
		self._fd = open(filepath, flags)

	def log(self, msg):
		if not self._fd:
			return
		self._fd.write(msg)

	def logline(self, msg):
		self.log(msg)
		self.log('\n')

	def close(self):
		if self._fd:
			self._fd.close()
			self._fd = None
	
class dataFlowLogger(Logger):# Scheduler.py
	def __init__(self, name):
		# name = 'snd.log' or 'rcv.log'
		self.filepath = LOG_FILE_BASE + name
		Logger.__init__(self, self.filepath)

	def start(self):
		self.logline('# Start of logging: ' + time.ctime())
		self.count = dict() # {(ip, asid): (timestamp, count)}

	def stop(self):
		for peer in self.count.keys():
                        curCount = self.count[peer]
                        self.logline('{0}; {1}; {2};'.format(peer, curCount[0], curCount[1]))
                self.logline('# End of logging: ' + time.ctime())
                self.close()
	
	def logPkt(self, remote, curTime, pkts_num):
		curTime = float('%{0}f'.format(LOG_PRECISION)%float(curTime))
		# convert the time to specified precision
		curCount = self.count.get(remote)
		if curCount == None:
			self.count[remote] = (curTime, pkts_num)
		elif curTime == curCount[0]:
			self.count[remote] = (curTime, curCount[1] + pkts_num)
		else:
			self.logline('{0}; {1}; {2};'.format(remote, curCount[0], curCount[1]))
			self.count[remote] = (curTime, pkts_num)


if __name__ == "__main__":
	l = dataFlowLogger()
	l.start()
	l.logPkt('("1.1.1.1", 3000)', '1111.111', '0.1', 10)
	l.logPkt('("1.1.1.1", 3000)', '1111.111', '0.1', 20)
	l.logPkt('("1.1.1.1", 3000)', '1112.111', '0.1', 30)
	l.stop()
	'''
	l = Logger("log/test.log")
	l.log("abc")
	l.logline("def")
	l.logline("ghi")
	l.close()

	import time
	l = Logger("log/timetest.log","a+")
	l.logline("%f ghi"%(time.time()))
	l.close()
	'''
