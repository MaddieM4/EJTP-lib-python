#!/bin/sh

python setup.py build
sudo rm -r `ls /usr/local/lib/python2.*/dist-packages/ejtp -d`
sudo python setup.py install
doctestall ejtp
python -m ejtp.tests.runner
