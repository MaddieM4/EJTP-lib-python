#!/bin/sh

python setup.py -q build
sudo rm -r `ls /usr/local/lib/python2.*/dist-packages/ejtp -d`
sudo python setup.py -q install
doctestall ejtp
python ejtp/tests/runner.py