#!/usr/bin/bash
start=2010
stop=2024
skip="2021 2023"
cd FitnessInference
for i in `seq $start $stop`
do  
    pass=0
    for j in $skip
    do
        if [ $i -eq $j ]
        then
            pass=1
        fi
    done
    if [ $pass -eq 0 ]
    then
        python rank_sequences.py --aln "./in/aln_RF-2009-${i}.fa" --plot True --outgroup "A/California/04/2009|2009-04-01|EPI_ISL_29618"
        python rank_sequences.py --aln "./in/aln_RF-2009-${i}_vac.fa" --plot True --outgroup "A/California/04/2009|2009-04-01|EPI_ISL_29618"
    fi
done
cd ..