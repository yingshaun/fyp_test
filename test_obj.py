from fabric.api import *
from config import *
from json import *

# global variables
tObj = None
env.roledefs = {
	'sender': [],
	'peers': []
}

class TObj(object):
	def __init__(self, config):
		self.config = config
	def check_config(self):
		if self.config['file_size'] not in FILE_SIZE:
			print 'file_size'
			return False
		if self.config['num_init_peer'] <= 0:
			print 'num_init_peer'
			return False
		if self.config['num_peer'] <= 0:
			print 'num_peer'
			return False
		if len(self.config['nodes']) <= 1:
			print 'nodes'
			return False
		if self.config['sender'] == None:
			self.config['sender'] = DEFAULT_SENDER
		elif self.config['sender'] not in self.config['nodes'].keys():
			print 'sender'
			return False
	def add_hosts(self):
		print 'add_hosts'
	def setup(self, isSnd):
		print 'setup'
	def start(self, isSnd):
		print 'start'
	def end(self, isSnd):
		print 'end'
	def getlog(self, isSnd):
		print 'getlog'

class Nep2pTest(TObj):
	def __init__(self, config):
		super(Nep2pTest, self).__init__(config)
	# inherited
	def check_config(self):
		super(Nep2pTest, self).check_config()
		if self.config['version'] not in NEP2P_VERSIONS:
			print 'nep2p_version'
			return False
		if self.config['config_path_base'] == '':
			self.config['config_path_base'] = NEP2P_PATH_BASE
		if self.config['log_file'] == '':
			self.config['log_file'] = NEP2P_LOG_PATH
		return True
	def add_hosts(self, sender, peers):
		self.sender = sender 	# [NAME, PORT, ASID, HOST]
		self.peers = peers		# [NAME, PORT, ASID, HOST]
#
# setup
#
	def setup(self, isSnd = True, job = 'all'):
		# job = ('putfile', 'update', 'all')
		if isSnd:
			self.gen_nep2p_files(
				[(x[3].split('@')[1], x[2]) for x in self.peers],
				self.sender[1],
				self.sender[2],
				self.config['log_file'])
			execute(self.setup_sender, job, role="sender")
		else:
			for p in self.peers:
				self.gen_nep2p_files([], p[1], p[2], self.config['log_file'])
				execute(self.setup_peer, job, host=p[3])
	def setup_sender(self, job):
		path = self.config['config_path_base']
		if job == 'putfile' or job == 'all':
			put('genfiles/*', path)
			with cd(path):
				run('dd if=/dev/urandom of=./{0}.dat bs={1} count=1'
					.format(self.config['file_size'], self.config['file_size']))
		if job == 'update' or job == 'all':
			with cd(path):
				run('python control.py update -v ' + self.config['version'])
	def setup_peer(self, job):
		path = self.config['config_path_base']
		if job == 'putfile' or job == 'all':
			put('genfiles/*', path)
		if job == 'update' or job == 'all':
			with cd(path):
				run('python control.py update -v ' + self.config['version'])
#
# start
#
	def start(self, isSnd = True):
		if isSnd:
			execute(self.start_sender, role="sender")
		else:
			execute(self.start_peer, role="peers")
	def start_sender(self):
		with cd(self.config['config_path_base']):
			run('python control.py start -f ' + self.config['file_size'] + '.dat')
	@parallel
	def start_peer(self):
		with cd(self.config['config_path_base']):
			run('python control.py start')
#
# getlog
#
	def getlog(self, isSnd = True):
		if isSnd:
			execute(self._getlog, 'sender_' + self.sender[0], role="sender")
		else:
			for p in self.peers:
				execute(self._getlog, 'peer_' + p[0], host=p[3])
	def _getlog(self, name):
		path = self.config['config_path_base']
		log  = self.config['log_file']
		with cd(path):
			run('python control.py stat')
		get(path + 'log/' + log + 'stat.json',
			'getfiles/' + log + 'stat_' + name + '.json')
#
# check
#
	def check(self, isSnd = True):
		if isSnd:
			execute(self._check, role="sender")
		else:
			execute(self._check, role="peers")
	@parallel
	def _check(self):
		with cd(self.config['config_path_base']):
			run('python control.py check')
#
# end
#
	def end(self, isSnd = True):
		if isSnd:
			execute(self._end, role="sender")
		else:
			execute(self._end, role="peers")
	@parallel
	def _end(self):
		with cd(self.config['config_path_base']):
			run('python control.py end -r s')
#
# clean
#
	def clean(self, isSnd = True):
		if isSnd:
			execute(self._clean, role="sender")
		else:
			execute(self._clean, role="peers")
	@parallel
	def _clean(self):
		with cd(self.config['config_path_base']):
			run('python control.py clean')
#
# generate files
#
	def gen_nep2p_files(self, nodes, port, asid, log_path):
		self.gen_nodes(nodes)
		self.gen_nep2p(port)
		self.gen_config(asid, log_path)
	def gen_nodes(self, nodes): # n in nodes == [IP, ASID]
		d = {}
		for n in nodes:
			d[n[0]] = n[1]
		json = dumps(d)
		# write to nodes.json
		f = open('genfiles/nodes.json', 'w')
		f.write(json)
		f.close()
	def gen_nep2p(self, port):
		f = open('nep2p/nep2p.json', 'r')
		d = loads(f.read())
		d['external_port'] = port
		json = dumps(d)
		f.close()
		# write to nep2p.json
		f = open('genfiles/nep2p.json', 'w')
		f.write(json)
		f.close()
	def gen_config(self, asid, log_path):
		f = open('nep2p/config.json', 'r')
		d = loads(f.read())
		d['asid'] = asid
		d['log_file_base'] = NEP2P_LOG_PATH + log_path
		json = dumps(d)
		f.close()
		# write to config.json
		f = open('genfiles/config.json', 'w')
		f.write(json)
		f.close()

class BtTest(TObj):
	def __init__(self, config):
		super(BtTest, self).__init__(config)
		self.tracker_name = 'udp://tracker.openbittorrent.com:80/announce'
		self.file_name = self.config['file_size'] + '.dat'
		self.torrent_name = self.config['file_size'] + '.dat.torrent'
	def check_config(self):
		super(BtTest, self).check_config()
		return True
	def add_hosts(self, sender, peers):
		self.sender = sender 	# [NAME, PORT, ASID, HOST]
		self.peers = peers		# [NAME, PORT, ASID, HOST]
#
# setup
#
	def setup(self, isSnd = True, job = 'all'):
		# job = ('putfile', 'genfile', 'gentorrent', 'gettorrent', 'all')
		if isSnd:
			self.gen_config()
			execute(self.setup_sender, job, role="sender")
		else:
			for p in self.peers:
				self.gen_config()
				execute(self.setup_peer, job, host=p[3])
	def setup_sender(self, job):
		if job == 'putfile' or job == 'all':
			put('genfiles/config.json', BT_PATH_BASE)
			put('genfiles/btControl.py', BT_PATH_BASE)
			put('genfiles/logger.py', BT_PATH_BASE)
			put('genfiles/statCollect.py', BT_PATH_BASE)
		if job == 'genfile' or job == 'all':
			with cd(BT_PATH_BASE + BT_DOWNLOADS_PATH):
				run('dd if=/dev/urandom of=./{0}.dat bs={1} count=1'
					.format(self.config['file_size'], self.config['file_size']))
		if job == 'gentorrent' or job == 'all':
			with cd(BT_PATH_BASE + BT_DOWNLOADS_PATH):
				run('transmission-create ' + self.file_name + 
					' -t ' + self.tracker_name + 
					' -o ' + self.torrent_name +
					' -c ' + '\'FYP: YM & YXH\'')
				run('mv ' + self.torrent_name + ' ../torrents ')
		if job == 'gettorrent' or job == 'all':
			get(BT_PATH_BASE + BT_TORRENTS_PATH + self.torrent_name, 'torrents/')
	def setup_peer(self, job):
		if job == 'putfile' or job == 'all':
			put('genfiles/config.json', BT_PATH_BASE)
			put('genfiles/btControl.py', BT_PATH_BASE)
			put('genfiles/logger.py', BT_PATH_BASE)
			put('genfiles/statCollect.py', BT_PATH_BASE)
		put('torrents/' + self.torrent_name, BT_PATH_BASE + BT_TORRENTS_PATH)

#
# show
#
	def show(self, isSnd = True, job = 'all'):
		# job = ('downloads', 'torrents', 'all')
		if isSnd:
			execute(self._show, job, role="sender")
		else:
			execute(self._show, job, role="peers")
	@parallel
	def _show(self, job):
		if job == 'downloads' or job == 'all':
			run('ls ' + BT_PATH_BASE + BT_DOWNLOADS_PATH)
		if job == 'torrents' or job == 'all':
			run('ls ' + BT_PATH_BASE + BT_TORRENTS_PATH)
#
# show_daemon
#
	def show_daemon(self, isSnd = True):
		if isSnd:
			execute(self._show_daemon, role="sender")
		else:
			execute(self._show_daemon, role="peers")
	@parallel
	def _show_daemon(self):
		run('ls ~/.config/')
#
# start
#
	def start(self, isSnd = True):
		if isSnd:
			execute(self._start, role="sender")
		else:
			execute(self._start, role="peers")
	@parallel
	def _start(self):
		with cd(BT_PATH_BASE):
			run('python btControl.py start -t \'file:///home/cuhk_inc_01/fyp/transmission/torrents/' + self.torrent_name + '\'')
#
# show_bt
#
	def show_bt(self, isSnd = True):
		# job = ('downloads', 'torrents', 'all')
		if isSnd:
			execute(self._show_bt, role="sender")
		else:
			execute(self._show_bt, role="peers")
	@parallel
	def _show_bt(self):
		run('transmission-remote -l')
#
# getlog
#
	def getlog(self, isSnd = True):
		if isSnd:
			execute(self._getlog, 'sender_' + self.sender[0], role="sender")
		else:
			for p in self.peers:
				execute(self._getlog, 'peer_' + p[0], host=p[3])
	def _getlog(self, name):
		log = self.config['log_file']
		with cd(BT_PATH_BASE):
			run('python btControl.py stat')
		get(BT_PATH_BASE + BT_LOGS_PATH + log + 'stat.json',
			'getfiles/' + log + 'stat_' + name + '.json')
#
# check
#
	def check(self, isSnd = True):
		if isSnd:
			execute(self._check, role="sender")
		else:
			execute(self._check, role="peers")
	@parallel
	def _check(self):
		pass
#
# end
#
	def end(self, isSnd = True):
		if isSnd:
			execute(self._end, role="sender")
		else:
			execute(self._end, role="peers")
	@parallel
	def _end(self):
		with cd(BT_PATH_BASE):
			run('python btControl.py end')
#
# clean_daemon
#
	def clean_daemon(self, isSnd = True):
		if isSnd:
			execute(self._clean_daemon, role="sender")
		else:
			execute(self._clean_daemon, role="peers")
	@parallel
	def _clean_daemon(self):
		with cd(BT_PATH_BASE):
			run('python btControl.py clean -t all')
#
# clean_file
#
	def clean_file(self, isSnd = True):
		if isSnd:
			execute(self._clean_file, role="sender")
		else:
			execute(self._clean_file, role="peers")
	@parallel
	def _clean_file(self):
		with cd(BT_PATH_BASE):
			run('rm downloads/' + self.file_name)
#
# gen_config
#
	def gen_config(self):
		d = {}
		d['log_precision'] = 1
		d['log_file_base'] = BT_LOGS_PATH + self.config['log_file']
		json = dumps(d)
		# write to config.json
		f = open('genfiles/config.json', 'w')
		f.write(json)
		f.close()
