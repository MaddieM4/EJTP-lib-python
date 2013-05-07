#!/bin/sh
default_count=10
count=$1
if [ "$count" = "" ]; then
    count=$default_count;
fi
echo '$' $count ping
python scripts/ejtp-benchmark $count ping
echo '$' $count ping pong
python scripts/ejtp-benchmark $count ping pong
echo '$' $count ping pong done
python scripts/ejtp-benchmark $count ping pong done
