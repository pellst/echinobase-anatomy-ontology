#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post processing of xpo-simple.obo to add the intersection_of based on the XPO id_map.csv and the xpo-simple.obo
This will need to be added into the xpo pipeline as a post processing step for the .obo file

Version 1.1: Python3 ready & --verbose CLI option
"""
__author__    = "Troy Pells"
__copyright__ = "Copyright 2020 Xenbase"
__license__   = "Apache v2.0"
__version__   = "1.1"
__Credit__    = "based on Python OBO parser from Uli Köhler, 2013"

import pandas as pd
import numpy as np
from __future__ import with_statement
from collections import defaultdict
import re



# setup id_map dataset 
# C:\tmp\xpo\id_map.tsv
infilenameGen = "C:\\tmp\\xpo\\id_map.tsv"
data_idmap_df = pd.read_csv(infilenameGen, sep='\t', low_memory=False)
#data_idmap_df.columns = ['id','iri']
data_idmap_df.head()


# parse out the XPO and XAO terms
data_idmap_df["XPO"] = data_idmap_df.iri.str.split("/").str[4]

segment_xpo_df = pd.DataFrame([x.rsplit('-', 1) for x in data_idmap_df.id.to_list()],columns=['xao_acc', 'xao_suffix'])

data_idmap_df["XAO"] = segment_xpo_df.xao_acc

#data_idmap_df.head()
mydict = {}
mydict = data_idmap_df.set_index('XPO')['XAO'].to_dict()




def processXAOTerm(xaoGivenTerm):
    """
   Transform the XAO info given with syntax of EQE
   id_map.csv has the following examples

        XAO:0004013-PATO:0005013-XAO:0003024
        XAO:0003249-PATO:0005020-XAO:0004513
        XAO:0005202-PATO:0001649
        XAO:0005202-PATO:0001469
        PATO:0000620-XAO:0000113
        PATO:0030005-XAO:0000113


        The base case is simply an XAO:nnnnnnn
        Then we see GO used, on its own and then in combination with XAO like this:
        The GO:nnnnnnn – XAO:nnnnnnnn

        GO:0030182-XAO:0003226
        GO:0045214-PATO:0000001-XAO:0000174

        GO:0016477-XAO:0000026
        GO:0008283
        GO:0031941-XAO:0000207


    """
    ret = "intersection_of: "
    #print(xaoGivenTerm)
    segments_count = xaoGivenTerm.count("-")
    segment_xao_count = xaoGivenTerm.count("XAO")
    segment_go_count = xaoGivenTerm.count("GO")
    segment_pato_count = xaoGivenTerm.count("PATO")
    if segments_count == 0:
        if xaoGivenTerm[:3] == "XAO":
            ret = ret + "RO_0000052("+xaoGivenTerm+") ! inheres in"
        else:
            ret = ret + xaoGivenTerm
    else: # we have a multi segment
        parts_list = re.split("-", xaoGivenTerm)
        print(parts_list)
        for i,x_seg in enumerate(parts_list):
        #for i in xrange(len(parts_list)):
            #print(i,parts_list[i])
            print(i, x_seg)
            if i == 0: 
                if x_seg[:3] == "XAO":
                    ret = ret + "RO_0000052(" + x_seg + ")"
                else:
                    ret = ret + x_seg 
            if i == 1: 
                ret = ret + "^"
                if x_seg[:3] == "XAO":
                    ret = ret + "RO_0000052(" + x_seg + ")"
                else:
                    ret = ret + "RO_0002573(" + x_seg + ")"
            if i == 2: 
                ret = ret + "^"
                if x_seg[:3] == "XAO":
                    ret = ret + "RO_0000052(" + x_seg + ")"
            if i == 3: 
                ret = ret + "^"
                if x_seg[:3] == "XAO":
                    ret = ret + "RO_0000052(" + x_seg + ")"                    
    #for key, value in ret.items():
    #    if len(value) == 1:
    #        ret[key] = value[0]
    return ret + "\n"

# Open both files
with open("C:\\tmp\\xpo\\xpo-simple.obo") as f_in, open("C:\\tmp\\xpo\\xpo-simple-out.obo", 'w') as f_out:
    # Write header unchanged
    header = f_in.readline()
    f_out.write(header)
    
    currentGOTerm = None
    withinTerm = "no"
    xaoTerm = "XAO:123456789"

    # Transform the rest of the lines
    for line in f_in:
        #line = line.strip()
        #if not line: continue #Skip empty
        if not line.strip():
            if withinTerm == "yes": 
                if xaoTerm != "XAO:123456789":
                     #f_out.write("relationship: inheres_in "+xaoTerm+" ! tbd\n")
                     f_out.write(processXAOTerm(xaoTerm))
            if currentGOTerm:
                print(currentGOTerm["id"])
            

        # we are testing without the \n and that is why we perform line.strip()
        if line.strip() == "[Term]":
            #if currentGOTerm: processGOTerm(currentGOTerm)
            currentGOTerm = defaultdict(list)
            withinTerm = "yes"
        elif line.strip() == "[Typedef]":
            #Skip [Typedef sections]
            currentGOTerm = None
            withinTerm = "no"
        else: #Not [Term]
            #Only process if we're inside a [Term] environment
            #if currentGOTerm is None: continue
            #if currentGOTerm:
            if withinTerm == "yes":
                key, sep, val = line.partition(":")
                if key == "id":
                    #print(val)
                    currentGOTerm[key].append(val.strip())
                    #xaoTerm = mydict["XPO_0100002"]
                    #xaoTerm = mydict.get(val.strip(), "XAO:123456789")
                    # we substitute the colon with underscore to match obo data syntax for XPO:nnnnn
                    xaoTerm = mydict.get(val.strip().replace(":", "_"), "XAO:123456789")
                    print(xaoTerm)
        #f_out.write(line.lower())
        f_out.write(line)
