#!/bin/bash

sudo yum -y install libffi
sudo yum -y install libffi-devel
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig/
wget -O cffi-0.6.tar.gz https://www.dropbox.com/s/5zazoqua7nf31t4/cffi-0.6.tar.gz
tar -xzf cffi-0.6.tar.gz
cd cffi-0.6
python setup.py build
sudo python setup.py install

cd ..
sudo rm -r cffi-0.6
rm cffi-0.6.tar.gz
