#!/bin/bash

mkdir ~/fyp/
cd ~/fyp/
wget -O wgetnep2p3.sh https://raw.github.com/xuancaishaun/fyp_test/master/scripts/wgetnep2p3.sh
sudo chmod +x wgetnep2p3.sh
sudo ./wgetnep2p3.sh
rm wgetnep2p3.sh

wget -O install_nep2p.sh https://raw.github.com/xuancaishaun/fyp_test/master/scripts/install_nep2p.sh
sudo chmod +x install_nep2p.sh
sudo ./install_nep2p.sh
rm install_nep2p.sh

wget -O install_cffi.sh https://raw.github.com/xuancaishaun/fyp_test/master/scripts/install_cffi.sh
sudo chmod +x install_cffi.sh
sudo ./install_cffi.sh
rm install_cffi.sh

wget -O install_openssh.sh https://raw.github.com/xuancaishaun/fyp_test/master/scripts/install_openssh.sh
sudo chmod +x install_openssh.sh
sudo ./install_openssh.sh
rm install_openssh.sh

wget -O install_simplejson.sh https://raw.github.com/xuancaishaun/fyp_test/master/scripts/install_simplejson.sh
sudo chmod +x install_simplejson.sh
sudo ./install_simplejson.sh
rm install_simplejson.sh

cd ~/fyp
mkdir transmission
cd transmission
mkdir downloads
mkdir torrents
mkdir logs

sudo chown -R cuhk_inc_01 ~/fyp/
