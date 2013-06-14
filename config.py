from json import loads

HOST_OPTIONS = ('setup', 'start', 'getlog', 'check', 'end', 'clean')
P2P_SYS = ('nep2p', 'bt', 'libswft')
FILE_SIZE = ('1K', '10K', '100K', '1M', '5M', '10M', '20M', '30M', '40M', '50M', '100M')
NEP2P_VERSIONS = ('a13', 'a17', 'a17_rudp')
DEFAULT_SENDER = 's8'

NEP2P_PATH_BASE = '~/fyp/fyp_nep2p/'
NEP2P_LOG_PATH = 'log/'
#CONFIG_PATH_BASE = '~/fyp/fyp_nep2p/'
#LOG_PATH_BASE = 'log/'

BT_PATH_BASE = '~/fyp/transmission/'
BT_DOWNLOADS_PATH = 'downloads/'
BT_TORRENTS_PATH = 'torrents/'
BT_LOGS_PATH = 'logs/'

pl_nodes = loads(open('nodes_addr.json', 'r').read())

resolver = {
}

def resolve(host_name):
	if host_name not in resolver.keys():
		if host_name in pl_nodes:
			return {
				"host": "cuhk_inc_01@" + pl_nodes[host_name][1],
				"type": "key",
				"key": "PlanetLabKey"
			}
		else:
			print 'Wrong host name'
			return False
	return resolver[host_name]
