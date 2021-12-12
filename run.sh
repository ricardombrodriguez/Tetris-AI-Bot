#!/bin/bash  

for i in {0..20};do
  python3 server.py --seed $RANDOM --port $(( $i + 6000 )) &
  sleep 0.2
  PORT=$(( $i + 6000 )) python3 student.py &
done
