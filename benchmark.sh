#!/bin/sh
count=${1-10}
echo '$' $count ping
python scripts/ejtp-benchmark $count ping
echo '$' $count ping pong
python scripts/ejtp-benchmark $count ping pong
echo '$' $count ping pong done
python scripts/ejtp-benchmark $count ping pong done
