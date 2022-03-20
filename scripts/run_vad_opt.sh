#!/bin/bash

# Be sure that this file has execution permissions:
# Use the nautilus explorer or chmod +x run_vad.sh

# Write here the name and path of your program and database
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
DIR_P2="$(dirname "$SCRIPT_DIR")"
DB=$DIR_P2/db.v4
CMD=$DIR_P2/bin/vad

for filewav in $DB/*/*wav; do
    # echo "**************** $filewav ****************"
    if [[ ! -f $filewav ]]; then 
	    echo "Wav file not found: $filewav" >&2
	    exit 1
    fi

    filevad=${filewav/.wav/.vad}

    if [[ $# -eq 5 ]]; then
        $CMD -1 $1 -2 $2 --min-voice $3 --min-silence $4 --n-init $5 -i $filewav -o $filevad || exit 1
    else
        $CMD -1 $1 -2 $2 -i $filewav -o $filevad || exit 1
    fi

# Alternatively, uncomment to create output wave files
#    filewavOut=${filewav/.wav/.vad.wav}
#    $CMD $filewav $filevad $filewavOut || exit 1

done

scripts/vad_evaluation_opt.pl $DB/*/*lab

exit 0
