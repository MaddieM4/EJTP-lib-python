#!/bin/sh

python setup.py build
sudo rm -r `ls /usr/local/lib/python*.*/dist-packages/ejtp -d`
sudo python setup.py install
doctestall ejtp && python ejtp/tests/runner.py && sh benchmark.sh
