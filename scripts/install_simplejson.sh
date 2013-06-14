#!/bin/bash

wget -O simplejson-3.3.0.tar.gz https://pypi.python.org/packages/source/s/simplejson/simplejson-3.3.0.tar.gz
tar -zxf simplejson-3.3.0.tar.gz
cd simplejson-3.3.0
sudo python setup.py build
sudo python setup.py install
cd ..
rm simplejson-3.3.0.tar.gz
sudo rm -r simplejson-3.3.0
