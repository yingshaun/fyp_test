#!/usr/bin/env python

import json, sys, subprocess, os

def flush(str):
	sys.stdout.write(str)
	sys.stdout.flush()

try:
	config = json.loads(open('config.json', 'r').read())
	version = config['version'] if 'version' in config else 'default'
	print 'Home folder is "~/fyp/%s"'%version
	print 'Will download from branch %s'%version
except IOError:
	print 'Error: No config.json found'
	sys.exit(0)

CMD_control = ['wget', '-O', 'genfiles/control.py', 'https://raw.github.com/xuancaishaun/fyp_test/' + version + '/control.py']
CMD_btControl = ['wget', '-O', 'genfiles/btControl.py', 'https://raw.github.com/xuancaishaun/fyp_test/' + version + '/btControl.py']
CMD_logger = ['wget', '-O', 'genfiles/logger.py', 'https://raw.github.com/xuancaishaun/fyp_test/' + version + '/logger.py']
CMD_statCollect = ['wget', '-O', 'genfiles/statCollect.py', 'https://raw.github.com/xuancaishaun/fyp_test/' + version + '/statCollect.py']

f = open(os.devnull, "w")

flush('Download: control.py               status: ')
r = subprocess.call(CMD_control, stderr=f)
if r==0: flush('Done')
else: flush('Failed')
print ''


flush('Download: btControl.py             status: ')
r = subprocess.call(CMD_btControl, stderr=f)
if r==0: flush('Done')
else: flush('Failed')
print ''

flush('Download: logger.py                status: ')
r = subprocess.call(CMD_logger, stderr=f)
if r==0: flush('Done')
else: flush('Failed')
print ''

flush('Download: statCollect.py           status: ')
r = subprocess.call(CMD_statCollect, stderr=f)
if r==0: flush('Done')
else: flush('Failed')
print ''
