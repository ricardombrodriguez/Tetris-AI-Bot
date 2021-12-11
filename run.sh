#!/bin/bash  

rm results.txt
touch results.txt
for i in {0..30};do
  python3 server.py --seed $RANDOM --port $(( $i + 6000 )) &
  sleep 0.5
  PORT=$(( $i + 6000 )) python3 student.py &
done
./run.sh