import json, argparse, time, signal
import transmissionrpc as tt
import signal, os
from subprocess import call
from logger import *

parser = argparse.ArgumentParser()
parser.add_argument('option', choices = ['update', 'clean', 'start', 'stat', 'end'], help = "")
parser.add_argument('-t', '--torrent', help = "Specify torrent name")
args = parser.parse_args()


NONE   = "\033[m"
GRAY   = "\033[1;30m"
RED    = "\033[1;31m"
GREEN  = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE   = "\033[1;34m"
PURPLE = "\033[1;35m"
CYAN   = "\033[1;36m"
WHITE  = "\033[1;37m"

def printf(msg, mark, color=NONE):
	print '{0}[{1:^10}] {2}{3}'.format(color, mark, msg, NONE)

class btLogger:
	def __init__(self):
		self.sndLogger = dataFlowLogger('snd.log')
		self.rcvLogger = dataFlowLogger('rcv.log')
		self.sndLogger.start()
		self.rcvLogger.start()

	def run(self, myID, tc):
		signal.signal(signal.SIGINT, self.bye)
		signal.signal(signal.SIGTERM, self.bye)
		while True:
			myTorrent = tc.get_torrents(myID)[0]
			if myTorrent.status == 'seeding':
				printf(myTorrent.status, 'STATUS', YELLOW)
			if myTorrent.status == 'downloading':
				printf(myTorrent.status, 'STATUS', GREEN)
			else:
				printf(myTorrent.status, 'STATUS', RED)
			for i in myTorrent.peers:
			#	print i['address'], time.time(), i['rateToClient']
				self.rcvLogger.logPkt((i['address'], 0), time.time(), i['rateToClient'])
				self.sndLogger.logPkt((i['address'], 0), time.time(), i['rateToPeer'])
			time.sleep(1)

	def __del__(self):
		self.sndLogger.stop()
		self.rcvLogger.stop()
		
	def bye(self, signum, frame):
		print '\nBye'
		self.__del__()
		exit(0)

if __name__ == "__main__":
	if args.option == 'update':
		call(['wget', '-O', 'update_bt.sh', 'https://raw.github.com/xuancaishaun/fyp_test/master/update_bt.sh'])
		call(['sudo', 'chmod', '+x', 'update_bt.sh'])
		call(['./update_bt.sh'])
		
	if args.option == 'start':
		# log down self pid
		d = {}
		d['pid'] = os.getpid()
		info_file = open('info.json', 'w+')
		info_file.write(json.dumps(d))
		info_file.close()

		# start logginr
		tc = tt.Client('localhost', port = 9091)
		tmp = tc.add_torrent(args.torrent, download_dir = 'downloads')
		myID = tmp.id
		myTorrent = tc.get_torrents(myID)[0]
		myTorrent.start()	# start downloading

		myLogger = btLogger()
		myLogger.run(myID, tc)	# end downloading
		#myLogger.__del__()
		
		signal.signal(signal.SIGINT, myLogger.bye)
		signal.signal(signal.SIGTERM, myLogger.bye)

	if args.option == 'clean':
		tc = tt.Client('localhost', port = 9091)
		torrents = tc.get_torrents()
		for i in torrents:
			h = i.hashString
			tc.remove_torrent(h)

	if args.option == 'stat':
		printf('Executing statCollect.py', 'INFO', YELLOW)
		try:
			with open(os.devnull, "w") as f:
			# Write the output to the electronic trash can
				r = call(['python','statCollect.py','config.json'], stdout=f, stderr=f)
			if r == 0: printf('Success!', 'INFO', GREEN)
			else: printf('No such files: statCollect.py or config.json', 'ERROR', RED)
		except: 
			printf('Call Failed!', 'ERROR', RED)
		f.close()

	if args.option == 'end':
		try: info = json.loads(open('info.json','r').read())
		except: 
			printf('No info.json', 'ERROR', RED)
			exit(0)

		if 'pid' in info and info['pid'] > 0:
			call(['kill', str(info['pid'])])
			printf('Logger is killed: %s'%info['pid'],'INFO',GREEN)
