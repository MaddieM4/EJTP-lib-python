#!/bin/sh

echo "banana" | ejtp-crypto encode id mitzi@lackadaisy.com > nanafile.txt
cat nanafile.txt | ejtp-crypto decode id mitzi@lackadaisy.com

rm nanafile.txt