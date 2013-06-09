#!/bin/bash

if [ "$1" == "-h" ]; then
	echo "Usage: `basename $0` --option"
	exit 0
fi


if [ "$1" == "a17" ]
then
	wget -O lib/external_gateway.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/external_gateway.py
	wget -O lib/internal_gateway.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/internal_gateway.py
	wget -O lib/scheduler.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/scheduler.py
	wget -O lib/app_worker.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/app_worker.py
	wget -O lib/gateway.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/gateway.py
	wget -O lib/appsocket.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/appsocket.py
	wget -O lib/connection.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/connection.py
	wget -O lib/batch_acknowledger.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/batch_acknowledger.py
	
	wget -O lib/util/ip.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/ip.py
	wget -O lib/util/bmessage.py https://raw.github.com/xuancaishaun/fyp_test/a17/codes/bmessage.py

	wget -O lib/util/logger.py https://raw.github.com/xuancaishaun/fyp_test/a17/logger.py
	wget -O statCollect.py https://raw.github.com/xuancaishaun/fyp_test/a17/statCollect.py
	wget -O run.py https://raw.github.com/xuancaishaun/fyp_test/a17/run.py
	wget -O cli.py https://raw.github.com/xuancaishaun/fyp_test/a17/cli.py
fi
