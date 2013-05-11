#!/usr/bin/env python
import json
import argparse
from subprocess import *
from time import sleep
import os, sys, signal
from urllib import urlretrieve 

parser = argparse.ArgumentParser()
parser.add_argument('option', choices = ['update', 'start', 'check','status', 'end', 'quit', 'stat'], help = "")
parser.add_argument('-f', '--dataFile', help = 'sender: file to send')
parser.add_argument('-r', '--role', choices = ['s', 'c'], help = 'Role: service / client')
parser.add_argument('-v', '--version', choices = ['a16', 'a13', 'a16_rudp'], help = 'Version: nep2p2_a13/nep2p2_a16')
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

def bye(signum, frame):
	print '\nControl.py Exit'

if __name__ == '__main__':
	if args.option == 'update':
		call(['wget', '-O', 'update.sh', 'https://raw.github.com/xuancaishaun/fyp_test/master/update.sh'])
		call(['sudo', 'chmod', '+x', 'update.sh'])
		if args.version != None :
			call(['./update.sh', args.version])
		else:
			printf('Empty args.version', 'Error', RED)
		
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

	if args.option == 'start':
		f = open(os.devnull, "w")
		try:
			s_p = Popen(['python','run.py'])
			printf('Service started: %d'%s_p.pid, 'INFO', GREEN)
		except:
			printf('Failed to start Service!', 'ERROR', RED)
			sys.exit(1)

		#while True: if os.path.exists('/proc/%d'%s_p.pid): break
		sleep(3)

		try:
			if args.dataFile:
				c_p = Popen(['python','cli.py', args.dataFile])
				printf('Sender  started: %d'%c_p.pid, 'INFO', GREEN)
			else:
				c_p = Popen(['python','cli.py'])
				printf('Receiver  started: %d'%c_p.pid, 'INFO', GREEN)
		except Exception as e:
			printf('Failed to start clients!', 'ERROR', RED)
			print e.message
			sys.exit(1)

		d = dict()
		d['service_pid'] = s_p.pid
		d['client_pid'] = c_p.pid
		info_file = open('info.json', 'w+')
		info_file.write(json.dumps(d))
		info_file.close()

		signal.signal(signal.SIGINT, bye)
		signal.signal(signal.SIGTERM, bye)

		r1 = c_p.wait()
		printf('Client  is finished: %d, returncode: %s'%(c_p.pid, str(r1)), 'INFO', GREEN)
		r2 = s_p.wait()
		printf('Service is finished: %d, returncode: %s'%(c_p.pid, str(r2)), 'INFO', GREEN)
		sys.exit(0)

	if args.option == 'status':
		try: info = json.loads(open('info.json','r').read())	
		except: printf('No info.json', 'ERROR', RED)
		
		if args.role == 's':
			s_pid = info['service_pid']
                        if os.path.exists('/proc/%d'%s_pid):
                                printf('Service is alive: %d'%s_pid, 'INFO', GREEN)
                        else: printf('No such service: %d'%s_pid, 'INFO', YELLOW)
		elif args.role == 'c':
			c_pid = info['client_pid']
                        if os.path.exists('/proc/%d'%c_pid):
                                printf('Client  is alive: %d'%c_pid, 'INFO', GREEN)
                        else: printf('No such client: %d'%c_pid, 'INFO', YELLOW)
		else:
			s_pid = info['service_pid']
                        if os.path.exists('/proc/%d'%s_pid):
                                printf('Service is alive: %d'%s_pid, 'INFO', GREEN)
                        else: printf('No such service: %d'%s_pid, 'INFO', YELLOW)
			
			c_pid = info['client_pid']
                        if os.path.exists('/proc/%d'%c_pid):
                                printf('Client  is alive: %d'%c_pid, 'INFO', GREEN)
                        else: printf('No such client: %d'%c_pid, 'INFO', YELLOW)

	if args.option == 'check':
		try: info = json.loads(open('info.json','r').read())	
		except: printf('No info.json', 'ERROR', RED)

		c_pid = info['client_pid']
		while True:
			if os.path.exists('/proc/%d'%c_pid): continue
			else: 
				printf('Client is closed: %d'%c_pid, 'INFO', GREEN)
				break
			sleep(1)

	if args.option == 'end': # End the service when client is closed	
		try: info = json.loads(open('info.json','r').read())
                except: printf('No info.json', 'ERROR', RED)

		s_pid = info['service_pid']
                c_pid = info['client_pid']

		if args.role == 's' and os.path.exists('/proc/%d'%s_pid):
			call(['kill', str(s_pid)])
			printf('Service is killed: %d'%s_pid,'INFO',GREEN)
		elif args.role == 'c' and os.path.exists('/proc/%d'%c_pid):
			call(['kill', str(c_pid)])
			printf('Client  is killed: %d'%c_pid,'INFO',GREEN)
		else:
			while True:
				if os.path.exists('/proc/%d'%c_pid):
					#printf('Cannot kill service: Client(%d) is Alive'%c_pid,'INFO', YELLOW)
					sleep(2)
				else: 
					call(['kill', str(s_pid)])
					printf('Service is killed: %d'%s_pid,'INFO',GREEN)
					break


	if args.option == 'quit': # End both service and client process
		try: info = json.loads(open('info.json','r').read())
                except: printf('No info.json', 'ERROR', RED)
                s_pid = info['service_pid']
                c_pid = info['client_pid']
		r = call(['kill', str(s_pid)])
		if r == 0: printf('Service is killed: %d'%s_pid, 'INFO', GREEN)
		else: printf('Failed: no such service - %d'%s_pid, 'ERROR', RED)
		r = call(['kill', str(c_pid)])
		if r == 0: printf('Client  is killed: %d'%c_pid, 'INFO', GREEN)
                else: printf('Failed: no such client - %d'%c_pid, 'ERROR', RED)
