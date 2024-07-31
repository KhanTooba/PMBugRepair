from z3 import *

num_threads = 1
inf = 9999
lastStmt = 0

def printer(model, map):
    last = len(map)
    finalModel = []
    for i in range(1, last+1):
        for m in model:
            # print(m)
            if str(i) in str(model[m]) and not "pt" in str(m) and not "interleave" in str(m):
                # print(map[str(m)])
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
        elements = line.strip("[]\n").split(",")
        trace.append(parseTraceHelper(elements, counter))
        counter += 1

    return trace

def readBugs():
    return 0

def getIndividualThreads(trace):
    #Function to seperate out individual threads from one monolithic trace.
    indiThreads = []
    # print(num_threads)
    for i in range(num_threads):
        currentThread = []
        for j in range(len(trace)):
            if trace[j][-1]==i:
                currentThread.append(trace[j])
        indiThreads.append(currentThread)

    return indiThreads

def constructConstraint(i, j, s):
    a, b = 0, 0
    for s_i in s:
        if "pc_"+str(i) in str(s_i):
            # print(s_i, s[s_i])
            a = int(str(s[s_i]))
        if "pc_"+str(j) in str(s_i):
            # print(s_i, s[s_i])
            b = int(str(s[s_i]))
    
    if a<b:
        return Int("pc_"+str(i))<Int("pc_"+str(j))
    else:
        return Int("pc_"+str(i))>Int("pc_"+str(j))
    
def repairThread(thread):
    # print(thread)
    solver = Solver()
    map = {}
    adder = []
    blocking = []
    r = 1

    for i in range(len(thread)):
        if thread[i][1]==101:
            foundFlush = -1
            foundFence = -1
            for j in range(i+1, len(thread)):
                if thread[j][1]==102 and thread[i][2]==thread[j][2]:
                    foundFlush = 1
            if foundFlush==1:
                for j in range(i+1, len(thread)):
                    if thread[j][1]==103 :
                        foundFence = 1
            if foundFlush==-1:
                adder.append([str(thread[i][0])+"_"+str(r), 102, thread[i][2], '-1', thread[i][-1]])
                r += 1
            if foundFence==-1:
                adder.append([str(thread[i][0])+"_"+str(r), 103, 0, '-1', thread[i][-1]])
                r += 1

    for add in adder:
        thread.append(add)
    # print(thread)
    bug = []
    # print(adder)

    """
    Now, we have to build constraints:
    """
    
    length = len(thread)
    for i in range(length):
        #building phi_pc
        map["pc_"+str(i)] = thread[i]
        solver.add(Int("pc_"+str(i))>0, Int("pc_"+str(i))<length+1)
        for j in range(i+1, length):
            solver.add(Int("pc_"+str(i))!=Int("pc_"+str(j)))
        if thread[i][1]==101:
            #building phi_seq
            for j in range(i+1, length):
                if thread[j][1]==101:
                    solver.add(Int("pc_"+str(i))<Int("pc_"+str(j)))
            solver.add(Int("pt_"+str(i))>=Int("pc_"+str(i)))

            #building phi_pt
            for j in range(i+1, len(thread)):
                if thread[j][1]==102 and thread[i][2]==thread[j][2]:
                    foundFlush = j
            if foundFlush!=-1:
                for j in range(i+1, len(thread)):
                    if thread[j][1]==103 :
                        solver.add(Implies((And((Int("pc_"+str(i))<=Int("pc_"+str(foundFlush))),
                                                (Int("pc_"+str(foundFlush))<=Int("pc_"+str(j))))),
                                           (Int("pt_"+str(i))<=Int("pc_"+str(j)))))
                        blocking.append([i, foundFlush, j])
            
            #building phi_bug
            bug.append(Int("pt_"+str(i))<inf)
            for j in range(i+1, length):
                if thread[j][1]==101 and thread[i][1]==thread[j][2]:
                    bug.append(Int("pt_"+str(i))<Int("pt_"+str(j)))
    
    # print(bug)
    s = Solver()
    for assertion in solver.assertions():
        s.add(assertion)
    
    solver.add(Not(And(bug)))
    # print(solver.assertions())
    iter1 = 1
    while solver.check()==sat:
        model = solver.model()

        sai = []
        #we want a blocking constraint between every (store, flush, fence) pair
        for b in blocking:
            sai.append(constructConstraint(b[0], b[1], model))
            sai.append(constructConstraint(b[0], b[2], model))
            sai.append(constructConstraint(b[1], b[2], model))
        
        # print("ITERATION: ", iter1)
        # print(sai)
        iter1 += 1
        solver.add(Not(And(sai)))
        s.add(Not(And(sai)))
        if solver.check()==sat:
            model = solver.model()

    if s.check()==sat:
        m = s.model()
        repairedThread = printer(m, map)
    
    return repairedThread

def addConstraints(inputFileName, outputFileName):
    trace = parseTrace(inputFileName)
    writer = open(outputFileName, 'w+')
    global lastStmt
    lastStmt = len(trace)
    global num_threads
    num_threads = 2

    lastStmt = trace[-1][0]

    """
    Next steps:
    1. After reading a trace, first seperate trace into individual threads
    2. For each thread:
        a. Repair MPB, DURA bugs in the individual trace.
    3. Combine the resultant traces.
    """

    indiThreads = getIndividualThreads(trace) #seperated out the threads
    repaired_threads = []
    for i in range(num_threads):
        # print("Original Thread:")
        # print(indiThreads[i])
        repaired_threads.append(repairThread(indiThreads[i]))
        
    # print(lastStmt)

    """
    Finally, now we need to recombine the repaired threads
    """

    print("Beginning the recombination.")
    print()

    intermediateTrace = []
    # print(num_threads, repaired_threads)
    for i in range(num_threads):
        # print(repaired_threads[i])
        for stmt in repaired_threads[i]:
            intermediateTrace.append(stmt)
    # print(intermediateTrace)

    i = 1
    recombinedTrace = []
    while i<=lastStmt:
        for j in range(len(intermediateTrace)):
            if intermediateTrace[j][0]==i:
                recombinedTrace.append(intermediateTrace[j])

                while j+1<len(intermediateTrace):
                    if "_" in str(intermediateTrace[j+1][0]):
                        recombinedTrace.append(intermediateTrace[j+1])
                    j+=1
                i += 1
    
    return recombinedTrace

if __name__ == "__main__":
    inputFileName = "../inputFiles/"+sys.argv[1]         # "trace-1.txt"
    outputFileName = "../outputFiles/"+sys.argv[2]

    step1_result = addConstraints(inputFileName, outputFileName)

    for stmt in step1_result:
        print(stmt)
      
"""
Pending steps:
1. Automatically reading the number of threads
2. Automatically reading the bugs from a bug file
"""