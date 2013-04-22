import json

try:
	conf = json.loads(open("nep2p.json","r").read())
except:
	conf = {}

INTERNAL_PORT = conf['internal_port'] if 'internal_port' in conf else 22222
EXTERNAL_PORT = conf['external_port'] if 'external_port' in conf else 34567 #33333
HELPER_ASID = 0
SENDER = (0,0)

RESEND_STOP_INTERVAL = 15
REAL_STOP_INTERVAL = 30
UPDATE_INTERVAL = 2
KEEPALIVE_TIME = 30
REGULAR_INTERVAL = 0.000000001
RECODE_INTERVAL = 5
PKTLOG_INTERVAL = 1

INITIALIZED = 0
DECODING = 1
WAITING_FIN = 2
TO_BE_CLEARED = 3

BATCH_SIZE = 16
PACKET_SIZE = 1024
NETWORK_MIN_SIZE = 5 #if dst < 5: add helpers to expand to 5
BUF_SIZE = 2058


NONE   = "\033[m"
GRAY   = "\033[1;30m"
RED    = "\033[1;31m"
GREEN  = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE   = "\033[1;34m"
PURPLE = "\033[1;35m"
CYAN   = "\033[1;36m"
WHITE  = "\033[1;37m"


if __name__ == "__main__":
	print conf['congestion_gain'], conf['batchack_interval'], conf['congestion_target'], conf['congestion_threshold']
