import time
from z3 import *
from readBugs import *

"""
Questions to think:
1. Reading the bugs from a bug file
2. First repair all DURAs and then MPBs. What benefit does it give?-----No need for this
    It reduces the need to check for CLFLUSHOPT after stores while solving for MPB.
3. Add constraints for all statements belonging to the same line in the code.
"""

r = 0
inf = 9999
threads = {}
lastStmt = 0
num_fence = 0
num_flush = 0
fixedBugs = []
num_threads = 1
claimedFlushes = []
num_solverCalls = 0

def printer(model, map, thread):
    # print("Model: ",model)
    last = len(map)
    finalModel = []
    for i in range(1, last+1):
        # print("Searching for index: ",str(i))
        for m in model:
            if str(i)==str(model[m]) and not "pt" in str(m) and not "interleave" in str(m):
                # print(i, m, model[m], map[str(m)])
                finalModel.append(map[str(m)])
    
    return finalModel

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def printableSolver(solver):
    ref = {}
    for m in solver.model():
        ref[int(str(solver.model()[m]))] = m
        
    sorted_ref = dict(sorted(ref.items()))
    return sorted_ref

def printAllSolutions(s, lastStmt, writer):
    solver = Solver()
    solver.add(s.assertions())
    numSols = 0

    while solver.check()==sat:
        numSols += 1
        model = printableSolver(solver)
        writer.write(str(model))
        writer.write("\n")
        print(model)
        F = []
        for i in range(0, lastStmt):
            F.append(solver.model()[Int("var_"+str(i+1))]!=Int("var_"+str(i+1)))
        solver.add(Or(F))
    
    return numSols

def parseTraceHelper(elements, index):
    traceParsed = [index]
    if "LOAD" in elements[0]:
        traceParsed.append(100)
    elif "STORE" in elements[0]:
        traceParsed.append(101)
    elif "FLUSH" in elements[0]:
        traceParsed.append(102)
    elif "FENCE" in elements[0]:
        traceParsed.append(103)
    
    traceParsed.append(elements[1].strip())
    traceParsed.append(elements[2].strip())
    traceParsed.append(int(elements[3].strip()))
    traceParsed.append(elements[4].replace("'","").replace("\n", "").strip())
    # print(traceParsed)
    return traceParsed

def parseTrace(file):
    """
    Trace is used in the following format: 
    1. Trace is a 2-D array
    2. Each element of the trace array is a line in the original trace file i.e a program statement
    3. trace[i][0] = statement/line number 
    4. trace[i][1] = OPCODE (defined above)
    5. trace[i][2] = Target variable (Varible to be stored in case of STORE and FLUSH and a temporary variable in case of load)
    6. trace[i][3] = Value to be loaded (Value of importance in case of Loads)
    7. trace[i][4] = Thread ID
    """
    trace_file = open(file)
    trace = []
    counter = 1
    infoToSend = ""
    for line in trace_file:
        if counter==1:
            #Reading the thread info####
            global num_threads
            global threads
            num_threads = 2
            # Threads: [{'140255810307904': 0, '140255801911040': 1, '140255810303744': 2}]
            infoToSend = line
            threadInfo = line.replace("Threads: [{", "").replace("}]", "")
            for t in threadInfo.split(","):
                threads[t.split(":")[0].replace("'","").strip()] = int(t.split(":")[1].strip())
            num_threads = len(threads.keys())
            counter += 1
            continue
        elements = line.strip("[]\n").split(",")
        trace.append(parseTraceHelper(elements, counter))
        counter += 1

    # print("Returning from parceTrace.py")
    return trace, infoToSend

def addConstraints(inputFileName):
    trace, threadInfo = parseTrace(inputFileName)
    
    store = 0
    for t in trace:
        if t[1]==101:
            store += 1
    # print("Completed parsing.")
    global lastStmt
    lastStmt = len(trace)
    
    # lastStmt = trace[-1][0]
    # print("Local variables initialized.")

    bugs = []
    length = len(trace)
    mpbs, duras = [], []
    store = 0

    for i in range(length):
        # print(trace[i])
        if trace[i][1]==101:
            if str(trace[i][-1]) not in duras:
                bugs.append(Int("pt_"+str(trace[i][-1]))<inf)
                duras.append(str(trace[i][-1]))
            
            for j in range(i+1, length):
                if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]==trace[j][-2]:
                    if str(trace[i][-1]) not in mpbs:
                        first = "pt_"+str(trace[i][-1])
                        second = "pt_"+str(trace[j][-1])
                        bugs.append(Int(first)<Int(second))
                        mpbs.append(str(trace[i][-1]))
                        break

    # print("Number of bugs detected: ", len(bugs))
    for b in bugs:
        print(b)
    return bugs

if __name__ == "__main__":
    inputPath = "/Users/toobakhan/Downloads/PMBugRepair/results/outputs/"           #"_output.txt"
    outputPath = "/Users/toobakhan/Downloads/PMBugRepair/results/bugs/"             #memcached
    benchmarks = ["memcached", "CCEH", "array", "doublyList", "dqueue", "fastFair", 
                  "graph", "hash", "heap", "list_1", "list", "motivatingExample", 
                  "priorityQueue", "queue_1", "queue_2", "queue", "set", "skipLists", 
                  "stack", "stack_1", "P-CLHT"]
    for b in benchmarks:
        inputFile = inputPath+b+"_formatted_output.txt"
        outputFile = outputPath+b+"_1.txt"
        bugs = addConstraints(inputFile)
        f = open(outputFile, "w")
        for bug in bugs:
            f.write(str(bug)+"\n")
        f.close()