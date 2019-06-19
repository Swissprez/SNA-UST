# -*- coding: utf-8 -*-

#Check installation/use of these packages for windows
#Packages
import os
import json
import re
import snap
from operator import itemgetter
import csv

#File Handles
directory = 'C:\\Users\\Owner\\Dropbox\\GS_crawling_data\\CollectedAuthors' #raw json data
output = 'C:\\Users\\Owner\\Desktop\\SNA' #output for graphs

os.chdir(directory)

filepaths = [files for files in os.listdir(directory) if files.endswith(".json")] 
[i.split(",") for i in filepaths]
            
# Loads jsons into a list of dictionaries
jsons = []
for path in filepaths:
    with open(path,'r') as files:        
        for line in files:
            jsons.append(json.loads(line))

# Calculates size for edge matrix
size = 0
for files in jsons:
    size = size + len(files)
            
# =============================================================================
# Construction of userdict and nodedict
# userdict: author ID -> node ID
# nodedict: node ID -> author ID
# =============================================================================
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
nodedict = {x: y for y, x in userdict.items()} #dictonary of nodes to users

# =============================================================================
# author IDs from dataset file names
# =============================================================================
destnodes = [re.search('(.+?).json',path).group(1) for path in filepaths] 

jsonindex=0 #indexes list of jsons
sizeindex=0 #index for all the lines of the jsons

# =============================================================================
# Construction of edge matrix
# Each edge of the author citation network is taken from the raw json data
# A sample row of the edge matrix: Source Node, Destination Node, Edge Weight, Edge ID
# Destination Node: Author being cited (Author A)
# Source Node: Author I citing Author A
# Edge Weight: Number of citations made by Author I towards Author A
# Edge ID: unique ID of each edge
# =============================================================================
edge = [] #list of lists containing edges  
for jsonindex in range(len(jsons)): 
    DstNId = userdict[destnodes[jsonindex]] #source node id
    file = jsons[jsonindex]
    weights = jsons[jsonindex].values()
    rowindex=0
    for key in file:
        short = re.search('user=(.+?)&hl', key).group(1)
        SrcNId=userdict[short]  #source node of from row indexed in the current dataset
        edge.append([SrcNId,DstNId,weights[rowindex],sizeindex]) #source node, destination node, edge weight, edge id
        rowindex = rowindex + 1              #index for each keys in json
        sizeindex = sizeindex + 1            #row index of edge matrix

# =============================================================================
# Construction of the network
# =============================================================================
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

# =============================================================================
# self_citation function will find instances of self citations and return a list of lists where each list -> [nodeid, # of self citations]
# Inputs:
# destnodes: destination nodes, typically user IDs named in the file name of author citation datasets "jsons"
# edges: network edges (list of lists)
# jsons: list containing raw json data
# size: number of edges in network
# =============================================================================
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

# =============================================================================
# sum_citation will find the total number of citations by each author and return a list of lists where each list -> [nodeid, total # of citations]
# Inputs:
# destnodes: destination nodes, typically user IDs named in the file name of author citation datasets "jsons"
# edges: network edges (list of lists)
# size: number of edges in network
# =============================================================================
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

# =============================================================================
# self_citation_ratio returns the self citaiton ratio of each author in a list of lsits where each list -> [userid, self citation ratio]
# =============================================================================
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
os.chdir(output)

# =============================================================================
# printOutDegV will print outdegree for each node in the network
# =============================================================================
OutDegV = snap.TIntPrV()
snap.GetNodeOutDegV(G1, OutDegV)
def printOutDegV():
    for item in OutDegV:
        print "node ID %d: out-degree %d" % (item.GetVal1(), item.GetVal2())
    return

def printNumNodes(nodeid, reject):
    print("The number of unique authors is",nodeid,".")
    print("The number of non-unique occurences is",reject,".")
    return

# =============================================================================
# sortmatrix will return a sorted matrix or list of lists in ascending order given a designated column
# col: column number to sort by i.e. 0
# matrix: list of lists
# =============================================================================
def sortmatrix(matrix,col): #sort matrix in ascending order by col, timsort
    return sorted(matrix, key=itemgetter(col))

# =============================================================================
# Hash function will return a mapping of node IDs to edges associated with respective IDs
# i.e. node ID 0 -> edge[0:5]
# Inputs:
# sorteditem: edges sorted in asscending order
# col: col number to use for mapping
# =============================================================================
def asscedge(sorteditem,col): #hashing function
    size = len(sorteditem)
    asscTuple = {}
   #index = 0
    start = 0
    value = sorteditem[0][col]
    for index in range(size):
        if value != sorteditem[index][col]:
            finish = index - 1
            asscTuple[value]=(start,finish)
            start=index
            value = sorteditem[index][col]
        index += 1
    return asscTuple

# =============================================================================
# Function onehop generates a matrix (list of lists) containing one hop edges.
# Inputs:
# edge: edge matrix with a row composed of: Source node, Destination Node, No. of Citations, Edge ID
# userdict: dictionary converting from user IDs to integer node IDs
# =============================================================================
def onehop(edge, userdict):
    
    edgeSrc = sortmatrix(edge,0)  #edge matrix sorted by source nodes
    asscSrc = asscedge(edgeSrc,0) #returns associative array for edges with node id as key
    
    default = 0
    AtoB=[]
     
    for key in destnodes:
        destnodeID = userdict[key]
        startfinish = asscSrc[destnodeID] #start[0] finish[1]  #THIS WILL PRODUCE AN ERROR IF THE DESTINATION NODE DOES NOT CITE ANOTHER NODE
        for index in range(startfinish[0],startfinish[1]):
            AtoB.append(edgeSrc[index])
    
    AtoB = sortmatrix(AtoB,0) #sorts AtoB
    asscAtoB = asscedge(AtoB,0)
    
    BtoA=[]

    for row in AtoB:
        startfinish = asscSrc[row[1]]
        for index in range(startfinish[0],startfinish[1]):
            if row[0] == edgeSrc[index][1]:
               
                BtoA.append(edgeSrc[index])
    BtoA = sortmatrix(BtoA,0) #sorts BtoA
    #asscTupleBtoA = asscedge(BtoA,0)
    
    onestep = []
        
    
    for rowBtoA in BtoA:
         onestep.append(rowBtoA) #appends set B to A
         startfinish = asscAtoB.get(rowBtoA[1],default)
         if startfinish != 0 :
             for index in range(startfinish[0],startfinish[1]):
                 if AtoB[index][1] == rowBtoA[0]:
                     onestep.append(AtoB[index])
    
    return onestep        

# onestep = onehop(edge, userdict)
    
# =============================================================================
# Function onehopnetwork generates a SNAP network object containing one hop edges.
# Inputs: onestep
# 
# onestep: a matrix(list of lists) containing onehop edges
# =============================================================================
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

# G2 = onehopnetwork(onestep)

# =============================================================================
# Returns a directed Breadth-First-Search tree with root at startnode
# Inputs:
# G1: network
# nodekeys: keys of nodedict -> nodedict.keys()
# search(optional): if 0 -> generate 1 tree at startnode = nodeid
#         if 1 -> generate trees for all node ids
# startnode(optional): if search = 0: choose a root for the bfs tree using startnode
#         Do not use for search = 1
# FollowOut(Bool):
# FollowIn(Bool):
# =============================================================================
    
def getbfs(G1,nodekeys,search=0,startnode=0,FollowOut=True, FollowIn=False):
    bfstrees=[]
    if search == 0:
        bfstrees.append(snap.GetBfsTree(G1,startnode,FollowOut,FollowIn))
    if search == 1:
        for key in nodekeys:
            bfstrees.append(snap.GetBfsTree(G1,key,FollowOut,FollowIn))
    return bfstrees
    
# =============================================================================
# Function getnodesathops generates a dictionary of dictionaries with the outer dictionary 
# being a node key/ user id and the inner dictionary containing the number of nodes 
# at hop distance i where i is an integer.
# 
# G1: G1 is a snap network object
# nodedict: dictonary of node IDs (int) to user IDs (string)
# keychoice: 0 for node integer IDs, 1 for user string IDs
#
# example: hopobject = getnodesathops(G1,nodedict)
# =============================================================================
def getnodesathops(G1,nodedict, keychoice = 0):
    hops = {}
    
    for key in nodedict.keys():
        NodeVec = None
        NodeVec = snap.TIntPrV()
        snap.GetNodesAtHops(G1,key,NodeVec,True)
        inner = {}
        
        for item in NodeVec:
            inner[item.GetVal1()]=item.GetVal2()
        
        if keychoice == 0:
            hops[key] = inner
        else:
            hops[nodedict[key]] = inner
        
    return hops
        
# =============================================================================
# Function dictdump will dump the contents of a dictionary into a json file
# item: item should be a dictionary
# filename: should be a file name as a string with .json ending
# example: temp = dictdump(python_dictionary, 'contents.json')
# =============================================================================
def dictdump(item,filename):
    with open(filename, 'w') as fp:
        json.dump(item, fp)
    return

# =============================================================================
# Function matrixdump will dump the contents of a matrix (list of lists) into a csv file
# matrix: item should be a list of lists or matrix
# filename: should be a file name as a string with .csv ending
# example: temp = csvdump(list of lists, 'contents.csv')
# =============================================================================
def matrixdump(matrix,filename):
    with open(filename, "wb") as f:
        writer = csv.writer(f)
        writer.writerows(matrix)
    return
