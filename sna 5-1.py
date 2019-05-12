# -*- coding: utf-8 -*-

#Keys are citing the file name, reverse the edges

#Check installation/use of these packages
#Packages
import os
import json
import re
import snap
from operator import itemgetter
#import gnuplot 
#import graphviz
#import csv



#File Handles
directory = 'C:\\Users\\Owner\\Dropbox\\GS_crawling_data\\CollectedAuthors'

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
#cols = 4    #edge

edge = [] #initializes edge 
for jsonindex in range(len(jsons)): 
    DstNId = userdict[destnodes[jsonindex]] #integer source node id
    file = jsons[jsonindex]
    weights = jsons[jsonindex].values()
    rowindex=0
    for key in file:
        short = re.search('user=(.+?)&hl', key).group(1)
        SrcNId=userdict[short]  #this should be the contents of the json
        edge.append([SrcNId,DstNId,weights[rowindex],sizeindex]) #source node, destination node, edge weight, edge id
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

def self_citation(destnodes,edges,jsons,size): #parameters: edge,jsons
    self_cite = [] #initializes matrix
    for key in destnodes:
        match = userdict[key]
        count = 0
        for row in range(size):
            if match == edge[row][0] and match == edge[row][1] :
                count = count + edge[row][2]
        self_cite.append([match,count])
    return self_cite

self_cite = self_citation(destnodes,edge,jsons,size)

def sum_citation(destnodes,edge,size):
    sum_cite = []
    for key in destnodes:
        match = userdict[key]
        count = 0
        for row in range(size):
            if match == edge[row][0]:
                count = count + edge[row][2]
        sum_cite.append([match,count])
    return sum_cite
sum_cite = sum_citation(destnodes,edge,size)

def self_citation_ratio(nodedict, self_cite, sum_cite):
    #size = len(self_cite)
    self_cite_ratio = [] #initializes matrix
    for row in range(len(self_cite)):
        if self_cite[row][0] == sum_cite[row][0]:
            ratio = float(self_cite[row][1]) / float(sum_cite[row][1])
            self_cite_ratio.append([nodedict[self_cite[row][0]],ratio])
    return self_cite_ratio

self_cite_ratio = self_citation_ratio(nodedict, self_cite,sum_cite)
#output for graphs
os.chdir('C:\\Users\\Owner\\Desktop\\SNA')

#snap.SaveGViz(G1, "dot1Author.dot", "Graph file", labels)

OutDegV = snap.TIntPrV()
snap.GetNodeOutDegV(G1, OutDegV)
def printOutDegV():
    for item in OutDegV:
        print "node ID %d: out-degree %d" % (item.GetVal1(), item.GetVal2())
    return

def snap_self_citation_ratio(OutDegV,self_cite):
    size = len(self_cite)
    self_cite_ratio = [] #initializes matrix
    for item in OutDegV:
       for row in range(size):
           if item.GetVal1() == self_cite[row][0]:
               self_cite_ratio.append([item.GetVal1(),float(self_cite[row][1]) / float(item.GetVal2())])
    return self_cite_ratio
  
#snap_self_cite_ratio = snap_self_citation_ratio(OutDegV,self_cite)

def printNumNodes(nodeid, reject):
    print("The number of unique authors is",nodeid,".")
    print("The number of non-unique occurences is",reject,".")
    return

def totalSelfCite(edge):
    size = len(edge)
    self_cite = []
    for row in range(size):
        if edge[row][0] == edge[row][1]:
            self_cite.append([edge[row][0],edge[row][2]])
    return self_cite

total_self_cite = totalSelfCite(edge)

def totalSumCite(edge, nodedict): #need a sorting/search algo
    edgesize = len(edge)
    sum_cite = []
    for key in nodedict:
        count = 0
        for row in range(edgesize):
            if key == edge[row][0]: 
                count += edge[row][2]
        sum_cite.append([key,count])
    return sum_cite

def sortmatrix(matrix,col): #sort matrix in ascending order by col
    return sorted(matrix, key=itemgetter(col))

edgeSrc = sortmatrix(edge,0) #edge matrix sorted by source nodes

def hashedge(sorteditem,col): #hashing function
    size = len(sorteditem)
    hashed = {}
   #index = 0
    start = 0
    value = sorteditem[0][col]
    for index in range(size):
        if value != sorteditem[index][col]:
            finish = index - 1
            hashed[value]=(start,finish)
            start=index
            value = sorteditem[index][col]
        index += 1
    return hashed

hashedSrc = hashedge(edgeSrc,0)

def AtoBtoA(edgeSrc,userdict,hashedSrc):
    
    default = 0
    AtoB=[]
     
    for key in destnodes:
        destnodeID = userdict[key]
        startfinish = hashedSrc[destnodeID] #start[0] finish[1]  #THIS WILL PRODUCE AN ERROR IF THE DESTINATION NODE DOES NOT CITE ANOTHER NODE
        for index in range(startfinish[0],startfinish[1]):
            AtoB.append(edgeSrc[index])
    
    AtoB = sortmatrix(AtoB,0) #sorts AtoB
    hashedAtoB = hashedge(AtoB,0)
    
    BtoA=[]

    for row in AtoB:
        startfinish = hashedSrc[row[1]]
        for index in range(startfinish[0],startfinish[1]):
            if row[0] == edgeSrc[index][1]:
               
                BtoA.append(edgeSrc[index])
    BtoA = sortmatrix(BtoA,0) #sorts BtoA
    hashedBtoA = hashedge(BtoA,0)
    
    onestep = []
        
    
    for rowBtoA in BtoA:
         onestep.append(rowBtoA) #appends set B to A
         startfinish = hashedAtoB.get(rowBtoA[1],default)
         if startfinish != 0 :
             for index in range(startfinish[0],startfinish[1]):
                 if AtoB[index][1] == rowBtoA[0]:
                     onestep.append(AtoB[index])

#key error fml
    
    return onestep        

onestep = AtoBtoA(edgeSrc,userdict,hashedSrc)
    
def onehopnetwork(onestep):
    #find unique nodes in onestep
    nodes = []
    for row in onestep:
        if row[0] not in nodes:
            nodes.append(row[0])
        if row[1] not in nodes:
            nodes.append(row[1])
    
    #Creates network object
    G2 = snap.TNEANet.New()
    
    #Adds Nodes
    for node in nodes:
        G2.AddNode(node)
        
    #Adds Weight Attribute
    G1.AddIntAttrE('Weight')

    #Adds Edges
    for row in onestep:
        G2.AddEdge(row[0],row[1],-1) #AddEdge(SrcNId, DstNId, EId=-1) or EId = row[3]
        G2.AddIntAttrDatE(row[3],row[2],'Weight')   
    return G2

G2 = onehopnetwork(onestep)




#total_sum_cite = totalSumCite(edge,nodedict)
#################### OUTPUT ########################
#printNumNodes(nodeid, reject)
#printOutDegV() #many nodes
#print(total_self_cite)