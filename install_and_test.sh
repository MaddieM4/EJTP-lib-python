#!/bin/sh

set -e
python setup.py build
sudo python setup.py install
clear
python ejtp/test.py
