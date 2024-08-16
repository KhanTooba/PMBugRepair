import time
from z3 import *
"""
Questions to think:
1. Reading the bugs from a bug file
2. First repair all DURAs and then MPBs. What benefit does it give?
    It reduces the need to check for CLFLUSHOPT after stores while solving for MPB.
"""
num_threads = 1
inf = 9999
lastStmt = 0
threads = {}

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
    traceParsed.append(int(elements[4].replace("'","").strip()))
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
        elements = line.strip("[]\n").split(",")
        trace.append(parseTraceHelper(elements, counter))
        counter += 1

    print("Returning from parceTrace.py")
    return trace

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

def constructConstraint(i, j, s):
    a, b = 0, 0
    for s_i in s:
        # print("S_I: ", s_i)
        if "pc_"+str(i)==str(s_i):
            # print(s_i, s[s_i])
            a = int(str(s[s_i]))
        if "pc_"+str(j)==str(s_i):
            # print(s_i, s[s_i])
            b = int(str(s[s_i]))
    
    if a<b:
        return Int("pc_"+str(i))<Int("pc_"+str(j))
    else:
        return Int("pc_"+str(i))>Int("pc_"+str(j))

def sliceThread(thread):
    """
    How to do slicing?
    Only statements relevant to the bug should be present in the slice:

    How to recombine the slice?
    ...?
    """
    sliced = []
    return sliced

def repairDURA(thread, bug, previousConstraints):
    solver = Solver()
    map = {}
    blocking = []
    constraintsToReturn = []
    r = 0

    bugFlag = -1
    length = len(thread)
    print("Before append:", length)

    for i in range(len(thread)):
        # print(thread[i])
        if thread[i][1]==101:
            foundFlush = -1
            foundFence = -1
            if "pt_"+str(thread[i][0])!=str(bug).split("<")[0].replace(" ", ""):
                continue

            for j in range(i+1, length):
                if thread[j][1]==102 and thread[i][2]==thread[j][2]:
                    foundFlush = j
                    solver.add(Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[j][0]))-1)
                    constraintsToReturn.append(Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[j][0]))-1)
                    break
            
            for j in range(i+1, length):
                if thread[j][1]==103:
                    foundFence = 1 

            if "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", ""):
                # print(bug)
                if foundFlush==-1:
                    # print("Flush has not been found:", foundFlush)
                    flush = [str(thread[i][0])+"_"+str(r), 102, thread[i][2], thread[i][3], thread[i][4], thread[i][5]]
                    # print("Adding:", flush)
                    r += 1
                    thread.insert(i+1, flush)
                    solver.add(Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[i+1][0]))-1)
                    constraintsToReturn.append(Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[i+1][0]))-1)
                    bugFlag = 1

                if foundFence==-1:
                    # print("Fence has not been found.")
                    fence = [str(thread[i][0])+"_"+str(r), 103, '0', -1, thread[i][4], thread[i][5]]
                    # print("Adding:", fence)
                    # print(thread[i])
                    r += 1
                    thread.append(fence)
                    bugFlag = 1
    
    length = len(thread)
    print("After append:", length)
    print("The bug flag is:", bugFlag)
    if bugFlag==-1:
        return thread, constraintsToReturn
    # print(length)

    for i in range(length):
        map["pc_"+str(thread[i][0])] = thread[i]
        solver.add(Int("pc_"+str(thread[i][0]))>0, Int("pc_"+str(thread[i][0]))<length+1) #(0 <= pc_i <= max_stmt)
        
        for j in range(i+1, length):
            solver.add(Int("pc_"+str(thread[i][0]))!=Int("pc_"+str(thread[j][0]))) #(pc_i != pc_j ; if i!=j)

        if thread[i][1]==101: #Do this for all STORES
            for j in range(i+1, length):
                if thread[j][1]==101:
                    solver.add(Int("pc_"+str(thread[i][0]))<Int("pc_"+str(thread[j][0]))) #All STOREs must follow their original order
            
            solver.add(Int("pt_"+str(thread[i][0]))>=Int("pc_"+str(thread[i][0]))) #Persistent time begins at the time of STOREs
            
            #This relates to the DURA bugs
            if "pt_"+str(thread[i][0])!=str(bug).split("<")[0].replace(" ", ""):
                continue
            foundFlush = -1
            for j in range(i+1, len(thread)):
                if thread[j][1]==102 and thread[i][2]==thread[j][2]:
                    foundFlush = j
            if foundFlush!=-1:
                for j in range(i+1, len(thread)):
                    if thread[j][1]==103 :
                        if "pt_"+str(thread[i][0]) in str(bug):
                            solver.add(simplify(Implies((Int("pc_"+str(thread[i][0]))<Int("pc_"+str(thread[j][0]))),
                                                (Int("pt_"+str(thread[i][0]))<=Int("pc_"+str(thread[j][0])))
                                                )))
                            blocking.append([thread[i][0], thread[foundFlush][0], thread[j][0]])
    
    print("The number of assertions:", len(solver.assertions()))
    print("The number of blocking constraint will be: ", len(blocking))
    print("Blocking constraints:", blocking)
    
    s = Solver()
    for assertion in solver.assertions():
        s.add(assertion)
        # print(assertion)

    solver.add(Not(bug))
    print("Bug is:", Not(bug))
        
    iter1 = 1
    
    while solver.check()==sat:
        print("Num:", len(solver.assertions()))
        model = solver.model()
        # print(model)
        sai = []
        #we want a blocking constraint between every (store, fence) pair
        for b in blocking:
            sai.append(constructConstraint(b[0], b[2], model))
        
        print("ITERATION: ", iter1)
        # print(sai)
        iter1 += 1
        solver.add(Not(And(sai)))
        print(Not(And(sai)))
        s.add(Not(And(sai)))
        constraintsToReturn.append(Not(And(sai)))

        #(STORE(&x)->CLFLUSHOPT(&x))->.........->SFENCE()
    
    repairedThread = thread
    s.add(previousConstraints)
    # print("Constraints to send:", constraintsToReturn)
    # print("Previous constraints:", previousConstraints)
    models = []

    if s.check()==sat:
        model = s.model()
        repairedThread = printer(model, map, thread)
    
    for repaired in repairedThread:
        print(repaired)
    
    return repairedThread, constraintsToReturn

def repairMPB(thread, bug, previousConstraints):
    solver = Solver()
    map = {}
    blocking = []
    constraintsToReturn = []
    r = 0

    bugFlag = -1
    length = len(thread)
    print("Before append:", length)

    """
    What needs to be done?
    For every Store->Load dependency induced bug, i.e MPB kind of bugs->
        1. The PT_Store < PT_Load
        2. This constraint must be sent to the future bug repair calls
        3. This constraint needs to be added to the
    """

    for i in range(length):
        # print("pt_"+str(thread[i][1]))
        if thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", ""):
            # print(i)
            for j in range(i+1, length):
                if thread[j][1]==101 and "pt_"+str(thread[j][0])==str(bug).split("<")[1].replace(" ", ""):
                    # print("We found:", thread[i][0], thread[j][0])
                    bugFlag = 1
                    countFence = 0
                    for k in range(j+1, length):
                        if thread[k][1]==103:
                            # print("Fence found.")
                            countFence += 1
                    if countFence<2:
                        fence = [str(thread[i][0])+"_Fence_"+str(r), 103, '0', -1, thread[i][4], thread[i][5]]
                        # print("Adding:", fence)
                        # print(thread[i])
                        r += 1
                        thread.append(fence)
                    #Let us now make constraints:
                    # cons = Int("pt_"+str(thread[i][0]))<Int("pt_"+str(thread[j][0]))
                    # constraintsToReturn.append(cons)
                    # solver.add(cons)
                    break
    
    length = len(thread)
    print("After append:", length)
    print("The bug flag is:", bugFlag)
    if bugFlag==-1:
        return thread, constraintsToReturn
    
    for i in range(length):
        map["pc_"+str(thread[i][0])] = thread[i]
        solver.add(Int("pc_"+str(thread[i][0]))>0, Int("pc_"+str(thread[i][0]))<length+1) #(0 <= pc_i <= max_stmt)
        
        for j in range(i+1, length):
            solver.add(Int("pc_"+str(thread[i][0]))!=Int("pc_"+str(thread[j][0]))) #(pc_i != pc_j ; if i!=j)

        if thread[i][1]==101: #Do this for all STORES
            for j in range(i+1, length):
                if thread[j][1]==101:
                    solver.add(Int("pc_"+str(thread[i][0]))<Int("pc_"+str(thread[j][0]))) #All STOREs must follow their original order
            
            solver.add(Int("pt_"+str(thread[i][0]))>=Int("pc_"+str(thread[i][0]))) #Persistent time begins at the time of STOREs
            
            #This relates to the MPB bugs
            if not((thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", "")) or (
                thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[1].replace(" ", ""))): 
                continue
            #How do I construct blocking constraints for MPB Bugs
            if (thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", "")) or (
                thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[1].replace(" ", "")): 
                #Checking if the store is a part of the MPB Bug
                #If the store is a part of the MPB Bug, then we need to keep all the fences after it in the blocking constraint
                for j in range(i+1, len(thread)):
                    if thread[j][1]==103:
                        blocking.append([thread[i][0], thread[j][0]])
            
            foundFlush = -1
            for j in range(i+1, len(thread)):
                if thread[j][1]==102 and thread[i][2]==thread[j][2]:
                    foundFlush = j
            if foundFlush!=-1:
                for j in range(i+1, len(thread)):
                    if thread[j][1]==103 :
                        if "pt_"+str(thread[i][0]) in str(bug):
                            solver.add(simplify(Implies((Int("pc_"+str(thread[i][0]))<Int("pc_"+str(thread[j][0]))),
                                                (Int("pt_"+str(thread[i][0]))<=Int("pc_"+str(thread[j][0])))
                                                )))

    print("The number of assertions:", len(solver.assertions()))
    print("The number of blocking constraint will be: ", len(blocking))
    print("Blocking constraints:", blocking)
    
    s = Solver()
    for assertion in solver.assertions():
        s.add(assertion)

    solver.add(Not(bug))
    print("Bug is:", Not(bug))

    iter1 = 1
    # print("Constraint: ", solver.assertions())
    while solver.check()==sat:
        print("Num:", len(solver.assertions()))
        model = solver.model()
        
        sai = []
        #we want a blocking constraint between every (store, fence) pair
        for b in blocking:
            sai.append(constructConstraint(b[0], b[1], model))
        
        print("ITERATION: ", iter1)
        # print(model)
        # print(sai)
        iter1 += 1
        solver.add(Not(And(sai)))
        print(Not(And(sai)))
        s.add(Not(And(sai)))
        constraintsToReturn.append(Not(And(sai)))
        """
        Why are the sai constraints not adding up? 
        Why not giving me a different solution?
        """
        

        #(STORE(&x)->CLFLUSHOPT(&x))->.........->SFENCE()

    repairedThread = thread
    s.add(previousConstraints)
    # print("Constraints to send:", constraintsToReturn)
    # print("Previous constraints:", previousConstraints)
    models = []

    if s.check()==sat:
        model = s.model()
        repairedThread = printer(model, map, thread)
    for repaired in repairedThread:
        print(repaired)
    # repairedThread = thread
    return repairedThread, constraintsToReturn
    
def repairThread(thread, bugs):

    """
    Plan:
    1. List out all the bugs----Done in previous function
    2. For each bug:
        a. Create a solver. ----Done for DURA
        b. Solve it.        ----Done for DURA
    """
    cons = []
    for b in bugs:
        print("Repairing for bug:", b)
        if str(inf) in str(b):
            thread, cons_1 = repairDURA(thread, b, cons)
            for constraint in cons_1:
                cons.append(constraint)
        else:
            print("MPB Bug found:", b)
            thread, cons_1 = repairMPB(thread, b, cons)
            for constraint in cons_1:
                cons.append(constraint)
        print()

    return thread

def addConstraints(inputFileName, outputFileName):
    trace = parseTrace(inputFileName)
    store = 0
    for t in trace:
        if t[1]==101:
            store += 1
    print("Number of stores:", store)
    print("Completed parsing.")
    # writer = open(outputFileName, 'w+')
    global lastStmt
    lastStmt = len(trace)
    
    lastStmt = trace[-1][0]
    print("Local variables initialized.")

    """
    Next steps:
    1. After reading a trace, first seperate trace into individual threads
    2. For each thread:
        a. Repair MPB, DURA bugs in the individual trace.
    3. Combine the resultant traces.
    """
    bugs = []
    length = len(trace)
    mpbs, duras = [], []

    store = 0
    print(trace[0], trace[1], trace[2])
    for i in range(length):
        if trace[i][1]==101:
            if str(trace[i][-1]) not in duras:
                bugs.append(Int("pt_"+str(trace[i][0]))<inf)
                duras.append(str(trace[i][-1]))
            
            for j in range(i+1, length):
                if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]==trace[j][-2]:
                    if [str(trace[i][-1]), str(trace[j][-1])] not in mpbs:
                        bugs.append(Int("pt_"+str(trace[i][0]))<Int("pt_"+str(trace[j][0])))
                        mpbs.append([str(trace[i][-1]), str(trace[j][-1])])
    
    print("Number of bugs detected: ", len(bugs))
    for b in bugs:
        print(b)
    
    #We have all the unique bugs now
    print("Original trace:")
    storeSeqs = []
    for stmt in trace:
        # print(stmt)
        if stmt[1]==101:
            storeSeqs.append(stmt[0])
    # print("\n\n")
    time1 = time.time()
    time2 = time1
    indiThreads = getIndividualThreads(trace) #seperated out the threads
    repaired_threads = []
    for i in range(num_threads):
        print("################################################################################################")
        print("Working on Thread:", i, "(Length of thread : ", len(indiThreads[i]), "): ")
        repaired_threads.append(repairThread(indiThreads[i], bugs))
        time2 = time.time()
        print("Time taken to repair thread ", i, ": ", (time2-time1), " seconds.")
        print("################################################################################################")
        time1 = time2
    
    """
    Finally, now we need to recombine the repaired threads
    """

    print("Beginning the recombination.")

    intermediateTrace = []
    for i in range(num_threads):
        for stmt in repaired_threads[i]:
            intermediateTrace.append(stmt)

    # for stmt in intermediateTrace:
    #     print(stmt)
    # print("\n\n")
    recombinedTrace = []

    """
    How can recombination be corrected?
    Only look at the order of stores because we 
    ensure that the order of stores must be maintained.

    Print a store and everything after it untill you encounter another store.
    once you encounter another store,
    """
    for i in range(0, len(storeSeqs)):
        storeToFind = storeSeqs[i]
        for j in range(len(intermediateTrace)):
            if intermediateTrace[j][0]==storeToFind:
                recombinedTrace.append(intermediateTrace[j])
                # print(intermediateTrace[j])
                while j+1<len(intermediateTrace) and intermediateTrace[j+1][1]!=101:
                    recombinedTrace.append(intermediateTrace[j+1])
                    # print("Int: ", intermediateTrace[j+1])
                    j+=1
        

    # while i<=lastStmt:
    #     for j in range(len(intermediateTrace)):
    #         if intermediateTrace[j][0]==i:
    #             recombinedTrace.append(intermediateTrace[j])
    #             print(intermediateTrace[j])
    #             while j+1<len(intermediateTrace) and "_" in str(intermediateTrace[j+1][0]):
    #                     recombinedTrace.append(intermediateTrace[j+1])
    #                     print(intermediateTrace[j+1])
    #                     j+=1
    #     i += 1
            
    time3 = time.time()
    print("Time taken to recombine individual threads: ", (time3-time2), " seconds.")
    return recombinedTrace

if __name__ == "__main__":
    inputFileName = sys.argv[1]         # "trace-1.txt"
    outputFileName = sys.argv[2]

    step1_result = addConstraints(inputFileName, outputFileName)

    f = open(outputFileName, "w")
    for stmt in step1_result:
        f.write(str(stmt))
        f.write("\n")
    
    f.close()

"""
Time exceeding 4 hr limit. Optimizations:
1. Focusing on one bug at a time.
2. The clflushopt(&x) statement is fixed at the position right after STORE(&x).
3. 
"""
