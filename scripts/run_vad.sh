#!/bin/bash

# Be sure that this file has execution permissions:
# Use the nautilus explorer or chmod +x run_vad.sh

if [[ $# -ge 2 ]]; then
    ALPHA1=$1
    ALPHA2=$2
    DEFAULTS=0
else
    DEFAULTS=1
fi

# Write here the name and path of your program and database
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
DIR_P2="$(dirname "$SCRIPT_DIR")"
DB=$DIR_P2/db.v4
CMD=$DIR_P2/bin/vad

for filewav in $DB/*/*wav; do
#    echo
    echo "**************** $filewav ****************"
    if [[ ! -f $filewav ]]; then 
	    echo "Wav file not found: $filewav" >&2
	    exit 1
    fi

    filevad=${filewav/.wav/.vad}

    if [[ $DEFAULTS -eq 1 ]]; then
        $CMD -i $filewav -o $filevad || exit 1
    else
        $CMD -1 $ALPHA1 -2 $ALPHA2 -i $filewav -o $filevad || exit 1
    fi

# Alternatively, uncomment to create output wave files
#    filewavOut=${filewav/.wav/.vad.wav}
#    $CMD $filewav $filevad $filewavOut || exit 1

done

scripts/vad_evaluation.pl $DB/*/*lab

exit 0
