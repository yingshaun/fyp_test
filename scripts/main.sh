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

sudo chown -R cuhk_inc_01 ~/fyp/
