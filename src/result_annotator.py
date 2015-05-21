from __future__ import division
import networkx as nx
import matplotlib.pyplot as plt
import os
import re
from networkx import graphviz_layout
import operator
import numpy as np
from unittest.util import sorted_list_difference
import argparse
import ConfigParser
import pandas as pd

def __main__():
    # parse command-line arguments
    parser = argparse.ArgumentParser(description='Annotates result files from the enrichment tool with descriptions and links (generating HTML output)', version='0.1')
    parser.add_argument('-i', '--inputfile', type=str, help='file name of the enrichment output')
    parser.add_argument('-o', '--htmloutput', type=str, help='name of the output file to which html will be written')
    parser.add_argument('--verbose', type=int, default=1, help='verbosity level')
    args = parser.parse_args()
    assert(args.inputfile is not None)
    assert(args.htmloutput is not None)
    cfg_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../conf/settings.cfg')
    cfg = ConfigParser.ConfigParser()
    cfg.read(cfg_file)
    descr_file = cfg.get('visualization','description_file')
    res = {}
    enrichment_file_content = pd.read_csv(args.inputfile,delimiter='\t')
    enrichment_file_content = enrichment_file_content.sort(['p value'])
    with open(descr_file,"r") as descr:
        for line in descr:
             items = line.strip().split('\t')
	     key, values = items[0], items[2:]
             res[key.lower()] = values
	h = open(args.htmloutput, 'w')
	h.write('<!DOCTYPE html>\n<html>\n<head></head>\n<body>\n<style> #mytablestyle{font-family: "Arial", Sans-Serif; font-size: 12px; margin: 10px; text-align: left; border-collapse: collapse; border: 1px solid rgba(24,26,36,1);}\n#mytablestyle th{padding: 5px 10px; background: rgba(225,229,250,1); font-weight: 700; color: rgba(24,26,36,1);}\n#mytablestyle tbody{background: rgba(238,238,238,1);}\n#mytablestyle td{padding: 2px 10px; background: rgba(238,238,238,1); color: rgba(24,26,36,1); border-top: 1px dashed white;}\n#mytablestyle tbody tr:hover td{background: rgba(225,229,250,1);}\n</style>\n')
	h.write( '<table id="mytablestyle">\n')
	h.write( '<thead><tr><th>Drug Annotation</th><th>Description</th><th>Database</th><th>Adj. P-value</th><th>P-value</th><th>Odds ratio</th><th>N</th></tr></thead>\n<tbody>\n')
    no_enrichment_found = True
    #print enrichment_file_content
    
    for idx, row in enrichment_file_content.iterrows():
        items = row
        key, values = items[0], items[1:]
        if key.lower() in res:
            no_enrichment_found = False
            desc = res[key.lower()]
            print values
            if(desc[0] == "ATC"):
                key = key.upper()
            database_name = values['database']
            database_name_el = database_name.split("_")
            database_name_el[-1] = "(" + database_name_el[-1] + ")"
            database_name = " ".join(database_name_el)
#            h.write('<tr><td><a href="' + desc[2] + '" target="_blank">' + key + '</a></td><td>' + desc[1] + '</td><td>' +  + '</td><td>' + str(values[1]) + '</td><td>' + str(values[2]) + '</td><td>' + str(values[3]) + '</td><td>' + str(values[4]) + '</td></tr>')
            h.write('<tr><td><a href="' + desc[2] + '" target="_blank">' + key + '</a></td><td>' + desc[1] + '</td><td>' + database_name + '</td><td>' + str(values[1]) + '</td><td>' + str(values[2]) + '</td><td>' + str(values[3]) + '</td><td>' + str(values[4]) + '</td></tr>')
        else:
            no_enrichment_found = False
            h.write('<tr><td>' + key + '</td><td>No description available yet</td><td>' + str(values[0]) + '</td><td>' + str(values[1]) + '</td><td>' + str(values[2]) + '</td><td>' + str(values[3]) + '</td></tr>')
    if no_enrichment_found:
        h.write('<tr><td>No enrichment found for this chemical set</td><td></td><td></td><td></td><td></td><td></td></tr>')
    h.write('</tbody></table>\n</body>\n</html>')    
            
if __name__ == '__main__': __main__()


