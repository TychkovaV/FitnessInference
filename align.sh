#!/usr/bin/bash
start=2010
stop=2024
skip="2021 2023"
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
        echo ${i}
        sed -i 's/(/_/g' "./FitnessInference/in/RF-2009-${i}.fasta"    
        sed -i 's/)/_/g' "./FitnessInference/in/RF-2009-${i}.fasta"    
        sed -i 's/\./_/g' "./FitnessInference/in/RF-2009-${i}.fasta"    
        cat "./FitnessInference/in/RF-2009-${i}.fasta" "H1N1_vac.fa" > "tmp.fasta"
        mafft --auto "tmp.fasta" > "./FitnessInference/in/aln_RF-2009-${i}_vac.fa"
        mafft --auto "./FitnessInference/in/RF-2009-${i}.fasta" > "./FitnessInference/in/aln_RF-2009-${i}.fa"
    fi
done
rm "tmp.fasta"