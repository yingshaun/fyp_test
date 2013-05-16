import json, argparse, time
import transmissionrpc as tt
from logger import *
from subprocess import call

parser = argparse.ArgumentParser()
parser.add_argument('option', choices = ['update', 'clean', 'start', 'stat'], help = "")
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
		while True:
			myTorrent = tc.get_torrents(myID)[0]
			if myTorrent.status == 'seeding': break
			for i in myTorrent.peers:
				print i['address'], time.time(), i['rateToClient']
				self.rcvLogger.logPkt((i['address'], 0), time.time(), i['rateToClient'])
				self.sndLogger.logPkt((i['address'], 0), time.time(), i['rateToPeer'])
			time.sleep(1)

	def __del__(self):
		self.sndLogger.stop()
		self.rcvLogger.stop()

if __name__ == "__main__":
	if args.option == 'update':
		call(['wget', '-O', 'update_bt.sh', 'https://raw.github.com/xuancaishaun/fyp_test/master/update_bt.sh'])
		call(['sudo', 'chmod', '+x', 'update_bt.sh'])
		call(['./update_bt.sh'])
		
	if args.option == 'start':
		# start logginr
		tc = tt.Client('localhost', port = 9091)
		tmp = tc.add_torrent(args.torrent)
		myID = tmp.id
		myTorrent = tc.get_torrents(myID)[0]
		myTorrent.start()	# start downloading

		myLogger = btLogger()
		myLogger.run(myID, tc)	# end downloading
		myLogger.__del__()

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

		
