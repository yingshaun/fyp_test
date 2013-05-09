#!/bin/bash

/sbin/service sshd status 		#check if ssh-server is installed or not
sudo yum install openssh-server 	#install the package
sudo /sbin/service sshd restart		#start the service
