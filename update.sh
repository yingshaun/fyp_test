#!/bin/bash

if [ "$1" == "-h" ]; then
	echo "Usage: `basename $0` --option"
	exit 0
fi

if [ "$1" == "a13" ]
then
	wget -O lib/external_gateway.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/external_gateway.py
	wget -O lib/scheduler.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/scheduler.py
	wget -O lib/app_worker.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/app_worker.py

	wget -O lib/util/logger.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/logger.py

	wget -O statCollect.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/statCollect.py
	wget -O run.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/run.py
	wget -O cli.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/cli.py
	wget -O ddM16m8r92TO.txt https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_a13/ddM16m8r92TO.txt

elif [ "$1" == "a16" || "$1" == 'a16_rudp' ]
then
	wget -O lib/external_gateway.py https://raw.github.com/xuancaishaun/fyp_test/master/external_gateway.py
	wget -O lib/scheduler.py https://raw.github.com/xuancaishaun/fyp_test/master/scheduler.py
	wget -O lib/app_worker.py https://raw.github.com/xuancaishaun/fyp_test/master/app_worker.py
	wget -O lib/gateway.py https://raw.github.com/xuancaishaun/fyp_test/master/gateway.py
	wget -O lib/appsocket.py https://raw.github.com/xuancaishaun/fyp_test/master/appsocket.py

	wget -O lib/util/logger.py https://raw.github.com/xuancaishaun/fyp_test/master/logger.py
	wget -O lib/util/ip.py https://raw.github.com/xuancaishaun/fyp_test/master/ip.py

	wget -O statCollect.py https://raw.github.com/xuancaishaun/fyp_test/master/statCollect.py
	wget -O run.py https://raw.github.com/xuancaishaun/fyp_test/master/run.py
	wget -O cli.py https://raw.github.com/xuancaishaun/fyp_test/master/cli.py
	wget -O ddM16m8r92TO.txt https://raw.github.com/xuancaishaun/fyp_test/master/ddM16m8r92TO.txt

	if [ "$1" == "a16_rudp" ]
	then
		wget -O lib/appsocket.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_rudp/appsocket.py
		wget -O lib/gateway.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_rudp/gateway.py
		wget -O lib/rudp.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_rudp/rudp.py
		wget -O lib/run.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_rudp/run.py
	fi

fi
