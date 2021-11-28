#!/bin/bash  

i="0"
n="10"
while [ $i -eq $n ]
do
gnome-terminal -- python3 student.py
i=$[$i+1]
done