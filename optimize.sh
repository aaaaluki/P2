#!/bin/bash

wavFile="pav_4151.wav"
vadFile="pav_4151.vad"
labFile="pav_4151.lab"

for alpha1 in $(seq 0.5 0.5 1.5)
do 
    for alpha2 in $(seq 10 0.5 12)
    do
        echo -n "$alpha1, $alpha2 "
        # bin/vad -1 $alpha1 -2 $alpha2 -i $wavFile -o $vadFile
        # scripts/vad_evaluation.pl $labFile | grep "==="
        scripts/run_vad.sh $alpha1 $alpha2 | tail -n 2 | head -n 1
    done
done | sort -t : -k 2n | tail
