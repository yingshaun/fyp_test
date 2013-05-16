import json, argparse
import transmissionrpc as tt

parser = argparse.ArgumentParser()
parser.add_argument('option', choices = ['clean', 'start', 'end'], help = "")
parser.add_argument('-t', '--torrent', required = True, help = "Specify torrent name")
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

if __name__ == "__main__":
	if args.option == 'start':
		# start logging
		tc = tt.Client('localhost', port = 9091)
		pass
	if args.option == 'clean':
		tc = tt.Client('localhost', port = 9091)
		torrents = tc.get_torrents()
		for i in torrents:
			h = i.hashString
			tc.remove_torrent(h)

