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

elif [ "$1" == "a16" ] || [ "$1" == 'a16_rudp' ]
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
		wget -O run.py https://raw.github.com/xuancaishaun/fyp_test/master/nep2p2_rudp/run.py
	fi

elif [ "$1" == "a13_to_a16" ]
then
	sudo yum install libffi
	sudo yum install libffi-devel
	export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig/
	wget -O cffi-0.6.tar.gz https://www.dropbox.com/s/5zazoqua7nf31t4/cffi-0.6.tar.gz
	tar -zxf cffi-0.6.tar.gz
	cd cffi-0.6
	python setup.py build
	sudo python setup.py install
	cd ..
	wget -O nep2p2_a16.zip https://www.dropbox.com/s/sanoagaumn9iyd8/nep2p2_a16.zip
	sudo yum install unzip
	unzip nep2p2_a16.zip
	sudo rm -r __MACOSX
	sudo rm -r bats_clean
	cp fyp_nep2p/libbatscore.so nep2p2_ms3/
fi
