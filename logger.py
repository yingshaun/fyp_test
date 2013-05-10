import os, json, time
from math import floor

try: client_config = json.loads(open('config.json', 'r').read())
except: client_config = {}

LOG_FILE_BASE = client_config['log_file_base'].encode() if 'log_file_base' in client_config else 'log/default/'
LOG_PRECISION = client_config['log_precision'] if 'log_precision' in client_config else 1


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
		self.prevTime = self.formatTime(time.time())
		self.nextTime = self.prevTime + LOG_PRECISION
		Logger.__init__(self, self.filepath)

	def start(self):
		self.logline('# Start of logging: ' + time.ctime())
		self.count = dict() # {(ip, asid): count}

	def stop(self):
		for key in self.count.keys():
                        self.logline('{0}; {1}; {2};'.format(key, formatTime(time.time()), self.count[key]))
                self.logline('# End of logging: ' + time.ctime())
                self.close()

	def formatTime(self, t):
		if type(LOG_PRECISION) == type(1): return int(floor(t))
		else: return float('%{0}f'.format(LOG_PRECISION)%t)
	

	def logPkt(self, remote, curTime, pkts_num):
		#curTime = float('%{0}f'.format(LOG_PRECISION)%float(curTime))
		curTime = self.formatTime(curTime)
		if curTime < self.nextTime:
			try: self.count[remote] += pkts_num
			except KeyError: self.count[remote] = pkts_num
		else: 
			for key in self.count.keys(): 
				self.logline('{0}; {1}; {2};'.format(key, self.prevTime, self.count[key]))
				self.count[key] = 0
			self.count[remote] = pkts_num
			self.prevTime = self.nextTime
			self.nextTime += LOG_PRECISION

if __name__ == "__main__":
	l = dataFlowLogger('test.log')
	l.start()
	l.logPkt('("1.1.1.1", 3000)', time.time(), 10)
	l.logPkt('("1.1.1.1", 3000)', time.time(), 20)
	time.sleep(1)
	l.logPkt('("1.1.1.1", 3000)', time.time(), 30)
	time.sleep(1)
	l.stop()
	l.close()
