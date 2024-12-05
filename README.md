# FitnessInference: a little research based on https://github.com/rneher/FitnessInference 

Raw input data from GISAID: ./RF-2009-2024.fasta 

Previous file with duplicate secuences removed via SRAtoolbox: ./RF-2009-2024_noDup.fasta

fasta_filter.py script: splits RF-2009-2024_noDup.fasta into subsampels RF-2009-XXXX.fasta in ./FitnessInference/in

align.sh script: performs multiple alignment via MAFFT (./FitnessInference/in/RF-2009-XXXX.fasta > ./FitnessInference/in/aln_RF-2009-XXXX.fa)

**NB:** after multiple alignment is performed the sequences must be trimmed properely (was done via AliView)

run_method.sh: calls original method ./FitnessInference/rank_sequences.py with output stored in ./FitnessInference/out
