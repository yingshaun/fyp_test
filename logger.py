import os
import json

try:
	client_config = json.loads(open('config.json', 'r').read())
except:
	client_config = {}
	
RCV_LOG_FILE = client_config['rcv_log_file'].encode() if 'rcv_log_file' in client_config else 'log/default/rcv.log'
SND_LOG_FILE = client_config['snd_log_file'].encode() if 'snd_log_file' in client_config else 'log/default/snd.log'
STAT_LOG_FILE = client_config['stat_log_file'].encode() if 'stat_log_file' in client_config else 'log/default/stat.log'
APP_WORKER_LOG_FILE = client_config['app_worker_log_file'].encode() if 'app_worker_log_file' in client_config else 'log/default/app_worker.log'

class Logger:
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


if __name__ == "__main__":
	l = Logger("log/test.log")
	l.log("abc")
	l.logline("def")
	l.logline("ghi")
	l.close()

	import time
	l = Logger("log/timetest.log","a+")
	l.logline("%f ghi"%(time.time()))
	l.close()
