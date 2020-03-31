from collections import defaultdict
from myUtility import returnParameters
from myUtility import isValidCombo
from allpairspy import AllPairs
from zipfile import ZipFile as zf
import numpy as np
import sys
import json
import csv
import time
import ast
import xml.etree.cElementTree as et
import mu
import setting
import os


f2 = sys.argv[2]
f1 = sys.argv[3]
testValue = sys.argv[4]

# reading the values of the valueMap of all files from project
# finalValue = open("finalValue.txt", 'w+')

myProject = sys.argv[1].split("/")[-1].split("_")[0]
path = "/".join(sys.argv[1].split("/")[0:-1]).replace("Graph_json", "values/")

fileList = os.listdir(path)
superValues = {}

for file in fileList:
    if file.startswith(myProject):
        for line in open(path + str(file), 'r').readlines():
            v = ast.literal_eval(line)
            for iv in v:
                # print iv['k'], iv['v']
                superValues[iv['k']] = iv['v'].split(",")
            
print(superValues)

valueMap = sys.argv[5]
# valueMap = str(valueMap)
# valueMap = ast.literal_eval(valueMap)

# hcValues will be replaced by superValues
# superValues = {}
# for indMap in valueMap:
#     key = indMap['k']
#     value = indMap['v'].split(",")indMap['v'].split(",")
#     superValues[key] = value

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = defaultdict(list)
        self.allPaths = []

    def addEdge(self, u, v):
        self.graph[u].append(v)

    def printAllPathsUtil(self, u, d, visited, path):

        visited[u] = True
        path.append(u)

        if u == d:
            self.allPaths.append(np.array(path))
        else:
            for i in self.graph[u]:
                if visited[i] == False:
                    self.printAllPathsUtil(i, d, visited, path)

        path.pop()
        visited[u] = False

    def printAllPaths(self, s, d):
        visited = [False]*(self.V)
        path = []
        self.printAllPathsUtil(s, d, visited, path)

# Supply file name to open as command-line argument
# Helps pass parameter from app.js
# fileName = "../../files/Graph_json/" + sys.argv[1]
with open(sys.argv[1]) as f:
    data = json.load(f)

# Holds the filtered out information as 'data' has much of unnecessary info
a = data["elements"][0]["elements"][0]["elements"]

# Simple counters
countVertex = 0
countEdge = 0
startNodeId = -1

# Hashmap (source_target) => (edgeDecription)
edgeDictionary = {}

"""
### The ids generated are misleading but work fine
"""

# Vertex and Edge list store the attributes of every corrosponding member
edge = list()
vertex = list()

t = open("ttt.txt", 'w')
t.write("trial file")
t.close()

# IDs are changes according to custom usuage
for i in range(2, len(a)):
    if('style' in a[i]["attributes"]):
        if(a[i]["attributes"]["style"] == 'shape=ellipse'):
            startNodeId = int(a[i]["attributes"]["id"])
    if ('vertex' in a[i]["attributes"]):
        if(a[i]["attributes"]["vertex"] == '1'):
            countVertex = countVertex + 1
            vertex.append(a[i])
    if('edge' in a[i]["attributes"]):
        if (a[i]["attributes"]["edge"] == '1'):
            countEdge = countEdge + 1

            source = (a[i]["attributes"]["source"])
            target = (a[i]["attributes"]["target"])

            for q in range(0, len(vertex)):
                if(vertex[q]["attributes"]["id"] == source):
                    source = q
                if(vertex[q]["attributes"]["id"] == target):
                    target = q

            key = str(source) + "_" + str(target)
            edgeDictionary[key] = a[i]["attributes"]["myDescription"]
            edge.append(a[i])

# arr is a adjacency matrix vertexID (X) and vertexID (Y)
arr = np.zeros(shape=(countVertex, countVertex))

# Holds custom graph class that searches for every possible path
g = Graph(countVertex)

for i in range(2, len(a)):
    if('edge' in a[i]["attributes"]):
        if (a[i]["attributes"]["edge"] == '1'):
            source = (a[i]["attributes"]["source"])
            target = (a[i]["attributes"]["target"])

            for i in range(0, len(vertex)):
                if(vertex[i]["attributes"]["id"] == source):
                    source = i
                if(vertex[i]["attributes"]["id"] == target):
                    target = i

            #print ("Edge exists from", source, " to ", target)
            arr[source][target] = 1
            g.addEdge(source, target)

print(arr)

# Holds the start node ID
# Column = 0 => No incoming edge and thus start
myStart = np.array(np.where(~arr.any(axis=0))[0])

# Holds every leaf node ID
# Row = 0 => No further child and thus leaf
leafNodes = np.array(np.where(~arr.any(axis=1))[0])

# Holds those cell IDs that are isolated
incompleteNodeId = np.intersect1d(leafNodes, myStart)

if(len(incompleteNodeId) > 0):
    print("Some nodes are either isolated or miss out parent/child")


print("Leafnodes are : "),
for l in leafNodes:
    # Leaf ids are still misleading
    print(l),

print("\n")

# start is the start node i.e. source
start = 0

# Finds every path from start to leaf
for leaf in leafNodes:
    g.printAllPaths(start, leaf)

# Holds paths from source to every leaves
myAllPaths = g.allPaths

# Holds variable parameters for every scenario
parameters = []


# file_bdd = open("./../../files/bdd/" + sys.argv[2] + ".txt", "w+")
file_bdd = open(sys.argv[2], 'w+')
file_bdd.write("BDD PATHS\n")
file_bdd.close()
# file_bdd.write("BDD PATHS\n")

metaData = {}

print("BDD paths"),
# myAllPaths are all the scenarios possible
for pathsNumber in range(0, len(myAllPaths)):
    # IDs are still misleading
    metaData['description'] = "Scenario #" + str(pathsNumber)
    metaData['key'] = metaData['description'] + ".testdata" # + str(pathsNumber)
    metaData['scenarioNumber'] = str(pathsNumber)
    buf = ""
    print("\n")
    lastIndex = -1
    parameterScenario = []
    for indPathIndex in range(0, len(myAllPaths[pathsNumber])):
        file_bdd = open(sys.argv[2], 'a')
        if(indPathIndex == 0):
            print("SCENARIO: " + metaData['scenarioNumber'])
            file_bdd.write("SCENARIO:")
            # file_bdd.write(metaData['scenarioNumber'])
            file_bdd.write("\n")
            buf += "\nSCENARIO:\n" #+ metaData['scenarioNumber'] + "\n"

            print("Metadata: " + str(metaData))
            file_bdd.write("META-DATA: ")
            file_bdd.write(str(metaData))
            file_bdd.write("\n")
            buf += "META-DATA: " + str(metaData) + "\n"

            print("\tGiven "),
            file_bdd.write("\tGiven ")
            buf += "\tGiven "

            print(vertex[myAllPaths[pathsNumber][indPathIndex]]
                  ["attributes"]["myDescription"])
            file_bdd.write(vertex[myAllPaths[pathsNumber][indPathIndex]]
                           ["attributes"]["myDescription"] + "\n")
            buf += vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["myDescription"] + "\n"
        if(indPathIndex != 0):
            # Find edge number
            s = myAllPaths[pathsNumber][indPathIndex - 1]
            t = myAllPaths[pathsNumber][indPathIndex]

            key = str(s) + "_" + str(t)
            print("\tWhen "),
            file_bdd.write("\tWhen ")
            buf += "\tWhen " 
            print(edgeDictionary[key])
            file_bdd.write(edgeDictionary[key] + "\n")
            buf += edgeDictionary[key] + "\n"
            for param in returnParameters(edgeDictionary[key]):
                parameterScenario.append(str(param))
            print("\tThen "),
            file_bdd.write("\tThen ")
            buf += "\tThen "
            print(vertex[myAllPaths[pathsNumber][indPathIndex]]
                  ["attributes"]["myDescription"])
            file_bdd.write(vertex[myAllPaths[pathsNumber][indPathIndex]]
                           ["attributes"]["myDescription"] + "\n")
            buf += vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["myDescription"] + "\n"
            file_bdd.close()
            if((vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["myShared"] == '1')):
                # Pass mySharedFile to the first parameter
                
                fileName = vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["mySharedFile"]
                fileName = str(fileName[0:-4])
                
                projectName = sys.argv[1].split("/")[-1].split("_")[0]
                # fileName = projectName + "_" + fileName

                fileName = "/".join(sys.argv[1].split("/")[0:-1]) + "/" + projectName + "_" + fileName

                file_bdd_read = open(sys.argv[2], 'r')
                lines = file_bdd_read.readlines()
                
                pari = len(buf.split("\n")) - 1

                # lines = lines[: -(((indPathIndex + 1) * 2) + 1)]
                lines = lines[:-pari]
                # -6 represents the number of LAST lines to be overwritten
                # lines = lines[:-6]

                file_bdd_read.close()
                
                file_bdd_write = open(sys.argv[2], 'w')
                for l in lines:
                    file_bdd_write.write(l)
                file_bdd_write.close()
                
                mu.sharedCode(fileName, False, buf, sys.argv[2])
                
                buf = ""
    
    file_bdd = open(sys.argv[2], 'a')
    file_bdd.write("END\n")
    file_bdd.close()
    setting.parameters.append(parameterScenario)

"""
# hard coded values right now
hcValues = {
    "username": ["abc", "xyz", "helloWorld", "fooBar"],
    "password": ["qwe", "pqr", "asd", "123"],
    "choice": ["1", "2", "3", "4"]
}
"""
# file_pairwise = open("./../../files/pairwise/" + sys.argv[2] + ".txt", 'w+')
file_pairwise = open(sys.argv[3], 'w+')
file_pairwise.write("Pairwise\n")

print("\nPAIRWISE"),

# creating root element 
root = et.Element("root")

# Now running pairwise algorithm for individual scenarios
count = -1

test = open("test.txt", 'w+')
test.write(str(setting.parameters) + "\n")
test.close()


file = open(sys.argv[2], 'r')
start = False
parameters = []
for line in file.readlines():
    if "SCENARIO" in line:
        # print "Start"
        start = True
        parameterScenario = []
    if "END" in line and start is True:
        # print "End"
        start = False
        parameters.append(parameterScenario)
        parameterScenario = []
    if start is True:
        for word in line.split():
            if word.startswith("$[") or word.startswith("${"):
                parameterScenario.append(word[2:-1])

# print parameter
# for p in parameter:
#     print p

for indParameters in parameters:
    print("\n")
    count = count + 1
    #subelement
    scene = et.SubElement(root, "Scenario" + str(count))    

    value = []
    paramName = []

    file_pairwise.write("\n")
    for p in indParameters:
        value.append(superValues[p])
        paramName.append(p)
        file_pairwise.write(p + "\t")
    print(value)

    file_pairwise.write("\n")

    # filter_func takes a custom built function checking the constraints imposed on parameters
    # previously_tested ignores the tuples mentioned in the list if already tested
    # n is n-wise pairing. Set to 2
    # Set to [['a'], ['b']] as values are not yt confirmed

    try:
        for i, pairs in enumerate(AllPairs(value, previously_tested=[], n=int(sys.argv[5]))):
            testData = et.SubElement(scene, "testData")

            print("{:2d}: {}".format(i, pairs))
            file_pairwise.write("{:2d}: {}".format(i, pairs) + "\n")
            for viru in range(0, len(pairs)):
                et.SubElement(testData, paramName[viru]).text = str(pairs[viru])

    except ValueError:
        print("Parameter less than 2")
    finally:
        print("")


tree = et.ElementTree(root)
# tree.write("filename.xml")
tree.write(testValue)

file_bdd.close()
file_pairwise.close()

# Making the file pretty
fileRead = open(sys.argv[2], 'r')
lines = fileRead.readlines()
fileRead.close()
fileWrite = open(sys.argv[2], 'w')
for i in range(1, len(lines)):
    if (lines[i] == lines[i-1]):
        print("Not adding")
    else:
        lines[i].replace(" META-DATA", "META-DATA")
        print("Adding")
        fileWrite.write(lines[i])
fileWrite.close()
