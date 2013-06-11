#!/bin/bash

if [ "$1" == "" ]
then echo "Path needs to be specified (e.g. 'a17_demo' --> '~/fyp/a17_demo')"
else
	sudo chown -R cuhk_inc_01 nep2p2
	cd ~/fyp/nep2p2
	git checkout v1.0a17.1645
	cd ..
	sudo rm -r "$1"
	mkdir "$1"
	sudo cp -r nep2p2/* "$1"
	sudo chown -R cuhk_inc_01 "$1"

	cd ../nep2p2
	git checkout a17
	cd ..
	sudo cp control.py "$1"
fi
