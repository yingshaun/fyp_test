from json import loads
from test_obj import *

@task
def help():
	print '\nCommand: fab setup [s:o=Option][p:o=Option]'
	print '##fab setup: is needed for every command'
	print '\nsetup: setup a testing'
	print '\tsetup | setup=t,cf'
	print 's: sender operations'
	print '\to | o=setup | o=setup,job | o=start | o=check | o=end | o=getlog | o=clean'
	print 'p: peer operations'
	print '\to | o=setup | o=setup,job | o=start | o=check | o=end | o=getlog | o=clean'


@task
def s(o = 'setup', job = 'all'):
	if o == 'setup' or o == 'show':
		getattr(tObj, o)(True, job);
	else:
		getattr(tObj, o)(True);

@task
def p(o = 'setup', job = 'all'):
	if o == 'setup' or o == 'show':
		getattr(tObj, o)(False, job);
	else:
		getattr(tObj, o)(False);

@task
def setup(t = 'nep2p', cf = 'config.json', d = False, l = False):
	global tObj
	p2p_type = None
	config = None
	# check input
	print 'Check input...'
	if t not in P2P_SYS:
		print 'Wrong P2P system type'
		return
	else:
		p2p_type = t;
		print '\tP2P type:', p2p_type
	try:
		f = open(cf, 'r')
		config = loads(f.read())
		print '\tConfig file:', cf
	except:
		print 'Wrong configuration file'
		return

	d = d if bool(d) else False;
	l = l if bool(l) else False;

	# construct a test object
	if p2p_type == 'nep2p':
		tObj = Nep2pTest(config)
	elif p2p_type == 'bt':
		tObj = BtTest(config)

	# parse configuration
	print '\nCheck configuration file...'
	if not tObj.check_config():
		print 'Configuration file is invalid'
		return

	# setup roles
	print '\nSetup roles...'
	# sender & peers
	sender = [config['sender']] + config['nodes'].pop(config['sender'])
	peers = [[k] + v for k, v in config['nodes'].iteritems()][:config['num_peer']]
	keys = []

	# add sender to roledefs
	res_sender = resolve(sender[0])
	sender.append(res_sender['host'])
	if res_sender['type'] == 'password':
		env.passwords[res_sender['host']] = res_sender['pw']
	elif res_sender['type'] == 'key':
		keys.append(res_sender['key'])
	env.roledefs['sender'].append(res_sender['host'])
	
	# add peers to roledefs
	for p in peers:
		res = resolve(p[0])
		p.append(res['host'])
		if res['type'] == 'password':
			env.passwords[res['host']] = res['pw']
		elif res['type'] == 'key' and res['key'] not in keys:
			keys.append(res['key'])
		env.roledefs['peers'].append(res['host'])

	# add keys
	env.key_filename = keys
	print '\tsender:'
	print '\t\t' + str(sender)
	print '\tpeers:'
	for p in peers:
		print '\t\t' + str(p)
	print '\tkey:'
	print '\t\t' + str(env.key_filename)

	# add sender and peers to the test object
	tObj.add_hosts(sender, peers)


