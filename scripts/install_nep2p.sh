#/bin/bash

wget -O nep2p_32.tar.gz https://www.dropbox.com/s/pxdk8njp47kl6er/nep2p_32.tar.gz
tar -zxf nep2p_32.tar.gz
mv nep2p_32 fyp_nep2p
rm nep2p_32.tar.gz

cd fyp_nep2p
sudo cp libstdc++.so.6 /usr/lib/libstdc++.so.6

sudo yum install easy_install
sudo easy_install gevent

wget https://raw.github.com/xuancaishaun/fyp_test/master/control.py
python control.py update -v 'a13'

cd ..
wget https://www.dropbox.com/s/l5ebv64n9sk9cy6/nep2p2_ms3_32.tar.gz -O nep2p2_ms3.tar.gz
tar -zxf nep2p2_ms3.tar.gz
rm nep2p2_ms3.tar.gz
cd nep2p2_ms3
rm libbatscore.so
cp ../fyp_nep2p/libbatscore.so .
wget https://raw.github.com/xuancaishaun/fyp_test/master/control.py
python control.py update -v 'a16'
