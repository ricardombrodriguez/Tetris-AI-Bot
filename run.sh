#!/bin/bash  

for i in {0..25};do
  python3 server.py --seed $RANDOM --port $(( $i + 6000 )) &
  sleep 0.5
  PORT=$(( $i + 6000 )) python3 student.py &
done