from z3 import *
from traceHelper import *

"""
Reads trace files generated after step 1 and finds candidate MPA bugs to be repaired in step 2.
"""

def generateRepair(inputFileName):
    trace = parseTrace(inputFileName)
    global lastStmt
    global num_threads
    lastStmt = len(trace)
    bugInfos = {}

    firstOcc = {}
    for t in trace:
        if t[-1] not in firstOcc.keys():
            firstOcc[t[-1]] = t
    
    reads, writes = [], []
    length = len(trace)
    bugCount = 0
    bugCons = []
    cons = []
    mpas = []
    i = 0
    while i<length:
        if trace[i][1]==101:
            # print(trace[i])
            for j in range(i+1, length):
                if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]!=trace[j][-2] and trace[i][-1]!=trace[j][-1]:
                    
                    if [str(trace[i][-1]), str(trace[j][-1])] not in mpas and [str(trace[j][-1]), str(trace[i][-1])] not in mpas:
                        # print(trace[i], trace[j])
                        # print(trace[i], trace[j])
                        first = firstOcc[trace[i][-1]][-1]
                        second = firstOcc[trace[j][-1]][-1]
                        bugInfos[str(first)+"-"+str(second)] = [firstOcc[trace[i][-1]], firstOcc[trace[j][-1]]]
                        # bugInfos[str(second)+"-"+str(first)] = [firstOcc[trace[j][-1]], firstOcc[trace[i][-1]]]
                        
                        bugCount += 1

                        mpas.append([str(trace[i][-1]), str(trace[j][-1])])
                        if firstOcc[trace[i][-1]][0] not in writes:
                            writes.append(firstOcc[trace[i][-1]][0])
                        if firstOcc[trace[j][-1]][0] not in reads:
                            reads.append(firstOcc[trace[j][-1]][0])

                        bugCons.append(And(Int("pc_"+str(first))<Int("pc_"+str(second)),
                                        Int("pt_"+str(first))>Int("pc_"+str(second))))
        i+= 1
    return bugCons

if __name__ == "__main__":
    inputPath = "/Users/toobakhan/Downloads/PMBugRepair/results/results/"           #"_output.txt"
    outputPath = "/Users/toobakhan/Downloads/PMBugRepair/results/bugs/"             #memcached
    benchmarks = ["memcached", "CCEH", "array", "doublyList", "dqueue", "fastFair", 
                  "graph", "hash", "heap", "list_1", "list", "motivatingExample", 
                  "priorityQueue", "queue_1", "queue_2", "queue", "set", "skipLists", 
                  "stack", "stack_1", "P-CLHT"]
    for b in benchmarks:
        inputFile = inputPath+b+"_trace_repaired.txt"
        outputFile = outputPath+b+"_2.txt"
        bugs = generateRepair(inputFile)
        f = open(outputFile, "w")
        for bug in bugs:
            f.write(str(bug)+"\n")
        f.close()