# -*- coding: utf-8 -*-

#Keys are citing the file name, reverse the edges

#Check installation/use of these packages
#Packages
import os
import json
import re
import snap
#import gnuplot 
#import graphviz
import csv

#File Handles
directory = 'C:\\Users\\Owner\\Dropbox\\GS_crawling_data\\author_list'

os.chdir(directory)

directory_in_str = directory

filepaths = [files for files in os.listdir(directory_in_str) if files.endswith(".json")] #validate test file before uncommenting
[i.split(",") for i in filepaths]
            
# Loads jsons into a list of dictionaries
jsons = []
for path in filepaths:
    with open(path,'r') as files:        
        for line in files:
            jsons.append(json.loads(line))

# Calculates json size for edge matrix
size = 0
for files in jsons:
    size = size + len(files)
            
# Creates dictionary of unique nodes, user to node 
userdict = {}
nodeid = 0 #index of unique authors
reject = 0 #count of non-unique authors
for files in jsons:
    for key in files:
        short = re.search('user=(.+?)&hl', key).group(1)
        if short not in userdict: #key
            userdict[short] = nodeid #[key]
            nodeid = nodeid + 1
        else:
            reject = reject + 1
nodedict = {x: y for y, x in userdict.items()} #dictonary of node to user

destnodes = [re.search('(.+?).json',path).group(1) for path in filepaths] #dest node user string

jsonindex=0 #indexes list of jsons
sizeindex=0 #index for all the lines of the jsons
cols = 4    #edge matrix contains 4 columns

############ REDEFINITION OF VARIABLES
size = 1

edge = [[0 for x in range(cols)] for y in range(size)] #initializes matrix

#for jsonindex in range(len(jsons)): 
DstNId = userdict[destnodes[0]] #integer source node id
file = jsons[0]
weights = jsons[0].values()
rowindex=0
for key in file:
    short = re.search('user=(.+?)&hl', key).group(1)
    SrcNId=userdict[short]  #this should be the contents of the json
    edge[sizeindex][0]=SrcNId            #source node
    edge[sizeindex][1]=DstNId            #destination node
    edge[sizeindex][2]=weights[rowindex] #edge weight
    edge[sizeindex][3]=sizeindex         #edge id
    rowindex = rowindex + 1              #index for each keys in json
    sizeindex = sizeindex + 1            #row index of edge matrix

labels = snap.TIntStrH()
for index in range(sizeindex):
    #labels[index]=nodedict[edge[index][0]]
    labels.AddDat(index,nodedict[edge[index][0]])

#Creates network object
G1 = snap.TNEANet.New()

#Adds Nodes
for node in nodedict:
    G1.AddNode(node)

#Adds Weight Attribute
G1.AddIntAttrE('Weight')

#Adds Edges
for row in range(sizeindex):
    G1.AddEdge(edge[row][0],edge[row][1],edge[row][3]) #AddEdge(SrcNId, DstNId, EId=-1)
    G1.AddIntAttrDatE(edge[row][3],edge[row][2],'Weight')

'''
#Adds Name Attribute
G1.AddStrAttrN('Name')

#Adds Names
for node in nodedict.keys():
    G1.AddStrAttrDatN(node,nodedict[node],'Name')
'''

#output for graphs
os.chdir('C:\\Users\\Owner\\Desktop\\SNA')

#snap.SaveGViz(G1, "dotgraph.dot", "Graph file", labels)

#nodes = nodedict.keys()    
#with open('sna_nodes.csv', mode='w') as sna_nodes:
#    wr = csv.writer(sna_nodes, quoting=csv.QUOTE_ALL)
#    wr.writerow(nodes)
#
#nodes=nodedict.keys()
#with open('sna_nodes.csv', mode='w') as sna_nodes:
#    wr = csv.writer(sna_nodes, quoting=csv.QUOTE_ALL)
#    wr.writerow(nodes)
#nodelabels=nodedict.values()
#with open('node_labels.csv', mode='w') as node_labels:
#    wr = csv.writer(node_labels, quoting=csv.QUOTE_ALL)
#    wr.writerow(nodelabels)
#
#targetsa=[]
#for index in range(sizeindex):
#    targetsa.append(edge[index][1])
#with open('targets.csv',mode='w') as targets:
#    wr = csv.writer(targets, quoting=csv.QUOTE_ALL)
#    wr.writerow(targetsa)
#    
#weightsa=[]
#for index in range(sizeindex):
#    weightsa.append(edge[index][2])
#with open('weights.csv',mode='w') as weights:
#    wr = csv.writer(weights, quoting=csv.QUOTE_ALL)
#    wr.writerow(weightsa)
#    