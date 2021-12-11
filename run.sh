#!/bin/bash  

rm results.txt
touch results.txt
for i in {0..20};do
  python3 server.py --seed $RANDOM --port $(( $i + 6000 )) &
  python3 viewer.py --port $(( $i + 6000 )) --scale 2 &
  sleep 2
  PORT=$(( $i + 6000 )) python3 student.py &
done
