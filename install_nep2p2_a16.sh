#!/bin/bash

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
