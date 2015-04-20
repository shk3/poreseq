import sys
import os
from Bio import SeqIO
from Util import RegionInfo
from poisscpp import swalign

def merge_seqs(seq1, seq2, overlap):
    
    # assumes the last 1000 bases of seq1 and the first 1000 bases of seq2 overlap
    i0 = -1000
    i1 = 1000
    if len(seq1) < 1000:
        i0 = 0
    if len(seq2) < 1000:
        i1 = len(seq2)-1

    acc,inds = swalign(seq1[i0:],seq2[:i1])
    # put some constraints on the accuracy
    if acc < 0.70:
        raise Exception('Insufficient accuracy for overlap')
    # now put the break point halfway between
    inds = [x in inds if x[0]>0 and x[1]>0]
    imid = inds[int(len(inds)/2)]
    i0 += imid[0]
    i1 = imid[1]
    return seq1[:i0] + seq2[i1:]
    

def merge_fasta(fastafiles, fastaout):

    fragments = {}

    # loop through each given fasta file and load them
    for fasta in fastafiles:
        refs = SeqIO.index(fasta, "fasta")
        # go through each ref header in this file
        for ref in refs:
            # this header is a combination of the filename and the header
            # so let's parse it
            reg = RegionInfo(ref)
            # and put all corresponding pieces in a list, along with the sequence
            if reg.name not in headers:
                fragments[reg.name] = []
            fragments[reg.name].append((reg,str(refs[ref])))

    # now fragments contains hopefully all the pieces, let's put them together
    # one sequence at a time

    outfile = open(fastaout,'w')

    for ref in fragments:
        seqlist = fragments[ref]
        # first, sort the list in order of start index
        seqlist.sort(key=lambda x: x[0].start)
        # and now reduce down to a single sequence
        seq = reduce(merge_seqs, [x[1] for x in seqlist])
        outfile.write('>{}\n{}\n'.format(ref,seq))

    
