#!/bin/sh
echo '10 ping'
python scripts/ejtp-benchmark 10 ping
echo '10 ping/pong'
python scripts/ejtp-benchmark 10 ping pong
echo '10 ping/pong/done'
python scripts/ejtp-benchmark 10 ping pong done