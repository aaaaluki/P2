#!/bin/bash

for alpha1 in $(seq 0 1 10)
do 
    for alpha2 in $(seq 0 2 20)
    do
        echo -n "$alpha1, $alpha2 "
        scripts/run_vad.sh $alpha1 $alpha2 | tail -n 2 | head -n 1
    done
done | sort -t : -k 2n | tail
