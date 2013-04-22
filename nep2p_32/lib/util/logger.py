import os

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
