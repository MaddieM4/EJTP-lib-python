#!/bin/sh

echo "banana" | ejtp-crypto encode id mitzi@lackadaisy.com > nanafile.txt
cat nanafile.txt | ejtp-crypto decode id mitzi@lackadaisy.com

echo "banana" > nanafile.txt
ejtp-crypto encode id mitzi@lackadaisy.com -f nanafile.txt > nananafile.txt
ejtp-crypto decode id mitzi@lackadaisy.com -f nananafile.txt

rm nanafile.txt
rm nananafile.txt