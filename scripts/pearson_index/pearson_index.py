#!/usr/bin/env python

'''
Calculates pearson index given a list of RBPs & TCGA FPKM file 
'''

import argparse
import os
import shutil
from scipy.stats import linregress
import numpy as np

CORES = 32

def make_first_line(genes):
    line = ""
    for gene in genes:
        line = line + "\t" + gene.strip()
    line = line + "\n"
    return line

def process_block(genes_block, genes_fpkm, rbp_list, outfile):
    lines = ""
    for gene in genes_block:
        line = gene.strip()
        for rbp in rbp_list:
            if rbp not in genes_fpkm:
                line = line + "\t" + "N/A"
            else:
                gene_fpkm = genes_fpkm[gene]
                rbp_fpkm = genes_fpkm[rbp]
                result = linregress(gene_fpkm, rbp_fpkm)
                # if index is 2 --> rvalue
                # if index is 3 --> pvalue
                index = 2
                line = line + "\t" + str(result[index])
        lines = lines + line + "\n"
    
    outfile.write(lines)
    return

parser = argparse.ArgumentParser(
    description="Generates pearson correlation index for a given list of RBPs.")

parser.add_argument("fpkm_db", help=".csv file containing fpkm information \
                                    for all genes across all patients from the TCGA study. \
                                    MUST BE TAB-DELIMITED.")
parser.add_argument("rbp_list", help="List of rbps to calculate pearson index for.")
parser.add_argument("output_file", help="Path to output file. Maps rows to genes.")

args = parser.parse_args()

print ">> Extracting rbp list..."
rbp_list = []
with open(args.rbp_list, "r") as rbp_file:
    for line in rbp_file:
        rbp_list.append(line.strip())

print ">> Building fpkm table..."
genes_fpkm = {}
genes_list = []
with open(args.fpkm_db, "r") as db_file:
    _ = db_file.readline()
    for line in db_file:
        splitted = line.split("\t")
        gene_name = splitted[0].strip()
        genes_fpkm[gene_name] = map(lambda fpkm: float(fpkm.strip()), splitted[1:])
        genes_list.append(gene_name)

missing = []
# Find RBPs not in fpkm_db
for rbp in rbp_list:
    if rbp not in genes_fpkm:
        missing.append(rbp)

print ">> Generating pearson correlation matrix..."
with open(args.output_file, "w+") as output_file:
    first_line = make_first_line(rbp_list)
    output_file.write(first_line)

    blocks = np.array_split(np.array(genes_list), CORES)
    processes = []
    for block in blocks:
        process_block(block, genes_fpkm, rbp_list, output_file)

    print ">> Matrix generated."
    print ">> The following rbps were not found in the fpkm database:"
    for item in missing:
        print item

