#!/bin/bash

if [ "$1" == "-h" ]; then
	echo "Usage: `basename $0` --option"
	exit 0
fi


wget -O logger.py https://raw.github.com/xuancaishaun/fyp_test/a17/logger.py
wget -O statCollect.py https://raw.github.com/xuancaishaun/fyp_test/a17/statCollect.py

