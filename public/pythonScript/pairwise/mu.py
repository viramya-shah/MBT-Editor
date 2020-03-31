from collections import defaultdict
import numpy as np
import sys
import json
import setting

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

def returnParameters(str):
    parameters = []

    for word in str.split():
        if (word.startswith("$")):
            parameters.append(word[2:-1])

    return parameters

def sharedCode(fileName, flag, buffer, fileWrite):
    with open(fileName + ".json") as f:
        data = json.load(f)
    
    a = data["elements"][0]["elements"][0]["elements"]
    # Simple counters
    countVertex = 0
    countEdge = 0
    startNodeId = -1

    # Hashmap (source_target) => (edgeDecription)
    edgeDictionary = {}
    edge = list()
    vertex = list()

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

    # print(arr)

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
        for i in incompleteNodeId:
            print(vertex[i])

    
    # start is the start node i.e. source
    start = 0

    # Finds every path from start to leaf
    for leaf in leafNodes:
        g.printAllPaths(start, leaf)

    # Holds paths from source to every leaves
    myAllPaths = g.allPaths

    # Holds variable parameters for every scenario
    parameters = []
    
    metaData = {}
    # myAllPaths are all the scenarios possible
    for pathsNumber in range(0, len(myAllPaths)):
        # IDs are still misleading
        # print("\n")
        lastIndex = -1
        buf = ""
        buf += buffer
        parameterScenario = []
        metaData['description'] = "description"
        metaData['key'] = "key"
        metaData['scenarioNumber'] = "-1"
        
        file_bdd = open(fileWrite, 'a')
        file_bdd.write(str(buffer))
        file_bdd.close()
        
        for indPathIndex in range(0, len(myAllPaths[pathsNumber])):
            file_bdd = open(fileWrite, 'a')
            if(indPathIndex == 0):
                if(flag is True):
                    print("\tGiven "),
                    file_bdd.write("\n\tGiven ")
                    buf += "\n\tGiven "
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
                print("\n\t\tWhen "),
                file_bdd.write("\tWhen ")
                buf += "\tWhen "
                print(edgeDictionary[key])
                file_bdd.write(edgeDictionary[key] + "\n")
                buf += edgeDictionary[key] + "\n"
                for param in returnParameters(edgeDictionary[key]):
                    parameterScenario.append(str(param))
                print("\t\tThen "),
                file_bdd.write("\tThen ")
                buf += "\tThen "
                print(vertex[myAllPaths[pathsNumber][indPathIndex]]
                    ["attributes"]["myDescription"])
                file_bdd.write(vertex[myAllPaths[pathsNumber][indPathIndex]]
                            ["attributes"]["myDescription"] + "\n")
                buf += vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["myDescription"] + "\n"
                file_bdd.close()
                if((vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["myShared"] == "1")):
                    # Pass mySharedFile to the first parameter
                
                    myfileName = vertex[myAllPaths[pathsNumber][indPathIndex]]["attributes"]["mySharedFile"]
                    myfileName = str(myfileName[0:-4])
                    
                    projectName = sys.argv[1].split("/")[-1].split("_")[0]
                    # myfileName = projectName + "_" + myfileName

                    myfileName = "/".join(sys.argv[1].split("/")[0:-1]) + "/" + projectName + "_" + myfileName

                    file_bdd_read = open(fileWrite, 'r')
                    lines = file_bdd_read.readlines()
                    
                    pari = len(buf.split("\n")) - 1

                    # lines = lines[: -(((indPathIndex + 1) * 2))]

                    lines = lines[:-pari]

                    # -6 represents the number of LAST lines to be overwritten
                    # lines = lines[:-6]

                    file_bdd_read.close()
                    
                    file_bdd_write = open(fileWrite, 'w')
                    for l in lines:
                        file_bdd_write.write(l)
                    file_bdd_write.close()
                    
                    sharedCode(myfileName, False, buf, fileWrite)
                    
                    buf = ""
                    
        # print("END\n")
        file_bdd = open(fileWrite, 'a')
        file_bdd.write("END\n")
        file_bdd.close()
        setting.parameters.append(parameterScenario)
