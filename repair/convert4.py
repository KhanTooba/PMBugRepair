import time
from z3 import *
"""
Questions to think:
1. Reading the bugs from a bug file
2. First repair all DURAs and then MPBs. What benefit does it give?-----No need for this
    It reduces the need to check for CLFLUSHOPT after stores while solving for MPB.
3. Add constraints for all statements belonging to the same line in the code.
"""

r = 0
inf = 9999
lastStmt = 0
threads = {}
num_locks = 0
num_fence = 0
fixedBugs = []
num_threads = 1
lockedReads = []
lockedWrites = []
claimedFlushes = []
num_solverCalls = 0


def printer(model, map):
    # print("Model: ",model)
    last = len(map)
    finalModel = []
    for i in range(1, last+1):
        # print("Searching for index: ",str(i))
        for m in model:
            # print(i, m, model[m])
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
    # print(elements)
    traceParsed = [index]
    traceParsed.append(int(elements[0].strip()))
    traceParsed.append(elements[1].strip().replace("'",""))
    traceParsed.append(elements[2].strip().replace("'",""))
    traceParsed.append(elements[3].strip())
    traceParsed.append(elements[4].replace("'","").strip())
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
    for line in trace_file:
        if counter==1:
            #Reading the thread info####
            global num_threads
            global threads
            num_threads = 2
            # Threads: [{'140255810307904': 0, '140255801911040': 1, '140255810303744': 2}]
            threadInfo = line.replace("Threads: [{", "").replace("}]", "")
            for t in threadInfo.split(","):
                threads[t.split(":")[0].replace("'","").strip()] = int(t.split(":")[1].strip())
            num_threads = len(threads.keys())
            counter += 1
            continue
        
        elements = line.strip("[]\n").replace("\"", "").split(",")
        modifiedElements = parseTraceHelper(elements, counter)
        # print(modifiedElements)
        trace.append(modifiedElements)
        counter += 1

    # print("Returning from parceTrace.py")
    return trace

def print_UNSATCORE(solver):
    dict_solver = {}
    s = Solver()
    i = 1
    for a in solver.assertions():
        s.assert_and_track(a, 'c_'+str(i))
        dict_solver['c_'+str(i)] = a
        i += 1
    if s.check()==unsat:
        print(s.unsat_core())
        for c in s.unsat_core():
            print(dict_solver[str(c)], c)

def getIndividualThreads(trace):
    #Function to seperate out individual threads from one monolithic trace.
    indiThreads = []
    print("Number of threads: ", num_threads)
    for i in range(num_threads):
        currentThread = []
        for j in range(len(trace)):
            # print(trace[j])
            if trace[j][-2]==i:
                currentThread.append(trace[j])
        indiThreads.append(currentThread)

    return indiThreads

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
                        # bugCons.append(And(Int("pc_"+str(second))<Int("pc_"+str(first)),
                        #                 Int("pt_"+str(second))>Int("pc_"+str(first))))
        i+= 1

    # print("Number of bugs to be repaired: ", bugCount)
    # for b in bugCons:
    #     print(b)
    
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