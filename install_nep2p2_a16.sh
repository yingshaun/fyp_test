#!/bin/bash

sudo yum install libffi
sudo yum install libffi-devel
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig/
wget -O cffi-0.6.tar.gz https://www.dropbox.com/s/5zazoqua7nf31t4/cffi-0.6.tar.gz
tar -zxf cffi-0.6.tar.gz
wget -O nep2p2_a16.zip https://www.dropbox.com/s/sanoagaumn9iyd8/nep2p2_a16.zip
