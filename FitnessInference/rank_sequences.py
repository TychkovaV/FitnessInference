#!/usr/bin/env python 
#########################################################################################
#
# author: Richard Neher
# email: richard.neher@tuebingen.mpg.de
#
# Reference: Richard A. Neher, Colin A Russell, Boris I Shraiman. 
#            "Predicting evolution from the shape of genealogical trees"
#
#########################################################################################
#
# rank_sequences.py
# Run the fitness inference on sequences in an alignment. Output is going to be written
# to a folder named by current date and time.
# INPUT:
# --aln             name of the alingment file, fasta format. can be gzipped
# --outgroup        name of the outgroup sequence. has to in the alignment file
# other parameters specify parameters of the inference algorithm and are optional
#
#########################################################################################


import argparse

#########################################################################################
###parse the command line arguments
#########################################################################################
parser = argparse.ArgumentParser(description="rank sequences in a multiple sequence aligment")
parser.add_argument('--aln', type=str, required= True, help = 'alignment of sequences to by ranked')
parser.add_argument('--outgroup', type=str,required= True, help = 'name of outgroup sequence')
parser.add_argument('--eps_branch', default=1e-5, type=float, help='minimal branch length for inference')
parser.add_argument('--tau', default=0.0625, type=float, help='time scale for local tree length estimation (relative to average pairwise distance)')
parser.add_argument('--collapse', const = True, default=True, nargs='?', help='collapse internal branches with identical sequences')
parser.add_argument('--plot', const = True, default=False, nargs='?', help='plot trees')
params=parser.parse_args()
#########################################################################################

# irrelevant parameters not needed for the LBI
params.diffusion=1.0
params.gamma=1.0
params.omega = 1.0
print("Using time scale tau =",params.tau,"in units of the average pairwise distance between sequences")

# change time units from pairwise distance to pair coalescent time.
params.tau = params.tau*2


import matplotlib
matplotlib.use('pdf')
import sys,time,os,argparse
sys.path.append('./prediction_src')
from prediction_src.sequence_ranking import *
import prediction_src.tree_utils as tree_utils
from Bio import Phylo,AlignIO,SeqIO, Align
from matplotlib import pyplot as plt
import numpy as np

## matplotlib set up
mpl_params = {'backend': 'pdf',  
          'axes.labelsize': 20, 
          'font.size': 20,
'font.sans-serif': 'Helvetica',
'legend.fontsize': 18,
'xtick.labelsize': 16,
'ytick.labelsize': 16,
'text.usetex': False}
plt.rcParams.update(mpl_params)

##########################################################################################
def ofunc(fname, mode):
    '''
    custom file open that chooses between gzip and regular open
    '''
    if fname[-3:]=='.gz':
        import gzip
        return gzip.open(fname,mode)
    else:
        return open(fname,mode)
##########################################################################################


##########################################################################################
## read the alignment, identify the outgroup 
##########################################################################################
aln = Align.MultipleSeqAlignment([])
outgroup=None
with ofunc(params.aln, 'r') as alnfile:
    for sec_rec in SeqIO.parse(alnfile, 'fasta'):
        if sec_rec.name!=params.outgroup:
            aln.append(sec_rec)
        else:
            outgroup=sec_rec

if outgroup is None:
    print("outgroup not in alignment -- FATAL")
    exit()

#######################################################################################
## set up the sequence data set and run the prediction algorithm
#######################################################################################
seq_data = alignment(aln, outgroup, collapse=True)

prediction = sequence_ranking(seq_data, eps_branch_length=params.eps_branch, pseudo_count = 5,
                            methods = ['polarizer'], D=params.diffusion,
                            distance_scale = params.gamma, samp_frac = params.omega)

best_node = prediction.predict()
prediction.calculate_polarizers(mem=params.tau)

#######################################################################################
## output
#######################################################################################

# make directory to write files to
dirname = './out/'+params.aln.split("-")[2][0:4]+("_vac" if "vac" in params.aln else "")
if not os.path.isdir(dirname):
    os.mkdir(dirname)

# name internal nodes
for ni,node in enumerate(prediction.non_terminals):
    node.name = str(ni+1)

# write tree to file
Phylo.write(prediction.T, dirname+'/reconstructed_tree.nwk', 'newick')

# write inferred ancestral sequences to file
with open(dirname+'/ancestral_sequences.fasta', 'w') as outfile:
    for node in prediction.non_terminals:
        outfile.write('>'+node.name+'\n'+str(node.seq)+'\n')

## write sequence ranking to file
# terminal nodes
prediction.rank_by_method(nodes = prediction.terminals, method = 'polarizer');
with open(dirname+'/sequence_ranking_terminals.txt', 'w') as outfile:
    outfile.write('#'+'\t'.join(['name','rank', 'LBI'])+'\n')
    for node in prediction.terminals:
        outfile.write('\t'.join(map(str,[node.name, node.rank, node.polarizer]))+'\n')

# terminal nodes
prediction.rank_by_method(nodes = prediction.non_terminals, method = 'polarizer')
with open(dirname+'/sequence_ranking_nonterminals.txt', 'w') as outfile:
    outfile.write('#'+'\t'.join(['name','rank', 'LBI'])+'\n')
    for node in prediction.non_terminals:
        outfile.write('\t'.join(map(str,[node.name, node.rank, node.polarizer]))+'\n')

# plot the tree if desired
if params.plot:
    tree_utils.plot_prediction_tree(prediction, method='polarizer', internal=True, size=len(aln), metadata={'name':params.aln})
    plt.savefig(dirname+'/marked_up_tree.pdf')
    plt.savefig('./out/'+params.aln.split("/")[-1]+'.pdf')

