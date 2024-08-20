import time
from z3 import *
"""
Questions to think:
1. Reading the bugs from a bug file
2. First repair all DURAs and then MPBs. What benefit does it give?-----No need for this
    It reduces the need to check for CLFLUSHOPT after stores while solving for MPB.
3. Add constraints for all statements belonging to the same line in the code.
"""
num_threads = 1
inf = 9999
lastStmt = 0
threads = {}
claimedFlushes = []
fixedBugs = []
r = 0
lockedReads = []

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
    # print(elements)
    traceParsed = [index]
    traceParsed.append(int(elements[0].strip()))
    traceParsed.append(elements[1].strip().replace("'",""))
    traceParsed.append(elements[2].strip().replace("'",""))
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
        
        elements = line.strip("[]\n").replace("\"", "").split(",")
        modifiedElements = parseTraceHelper(elements, counter)
        # print(modifiedElements)
        trace.append(modifiedElements)
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

def RepairSingleBug(trace, bug, previousConstraints):
    global r
    global lockedReads
    repairedTrace = trace
    solver = Solver()
    constraintsToReturn = []
    mapStmts = {}
    blockingConstraints = [] #We want all pairs of {Store, Lock} and {Sfence, unlock}

    cons = []
    indiThreads = getIndividualThreads(trace)
    for thread in indiThreads:
        for i in range(len(thread)-1): #Building basic constraints: There has to be a strict dependency between each statement.
            # Now we can not rearrange statements.
            cons.append(Int("pc_"+str(thread[i][0])) < Int("pc_"+str(thread[i+1][0])))

    print("Number of basic constraints: ", len(cons))
    length = len(trace)

    t1, t2 = 0, 0
    for t in trace:
        if "pt_"+str(t[0])==str(bug).split("<")[0].replace(" ", ""):
            t1 = t
        if "pt_"+str(t[0])==str(bug).split("<")[1].replace(" ", ""):
            t2 = t
    print(bug)
    print(t1, t2)

    lock_1 = ["Lock_"+str(r), 105, "M1", -1, t1[4], t1[5]]
    unlock_1 = ["UnLock_"+str(r), 106, "M1", -1, t1[4], t1[5]]
    cons.append(Int("Lock_"+str(r))< Int("UnLock_"+str(r)))
    r += 1
    lock_2 = ["Lock_"+str(r), 105, "M1", -1, t2[4], t2[5]]
    unlock_2 = ["UnLock_"+str(r), 106, "M1", -1, t2[4], t2[5]]
    cons.append(Int("Lock_"+str(r))< Int("UnLock_"+str(r)))
    r += 1
    #Only these four statements can now be floating

    trace.append(lock_1)
    trace.append(unlock_1)
    trace.append(lock_2)
    trace.append(unlock_2)

    #Now, we generate blocking constraints:
    #1. We only need two (Store, Lock) pairs
    blockingConstraints.append([t1[0], lock_1[0]])
    blockingConstraints.append([t2[0], lock_2[0]])
    
    #We now build the remaining constraints
    for i in range(len(trace)):
        mapStmts["pc_"+str(trace[i][0])] = trace[i]
        cons.append(Int("pc_"+str(trace[i][0]))>0)
        cons.append(Int("pc_"+str(trace[i][0]))<length+1) #(0 <= pc_i <= max_stmt)
        cons.append(Int("interleave_"+str(trace[i][0]))>0)
        cons.append(Int("interleave_"+str(trace[i][0]))<length+1)

        for j in range(i+1, length):
            cons.append(Int("pc_"+str(trace[i][0]))!=Int("pc_"+str(trace[j][0]))) #(pc_i != pc_j ; if i!=j)
            cons.append(Int("interleave_"+str(trace[i][0]))!=Int("interleave_"+str(trace[j][0])))
        
        # if trace[i][1]==101 and ("pt_"+str(trace[i][0])==str(bug).split("<")[0].replace(" ", "") or 
        #                          "pt_"+str(trace[i][0])==str(bug).split("<")[1].replace(" ", "")): #do this for all STOREs
        #     cons.append(Int("pt_"+str(trace[i][0]))>=Int("pc_"+str(trace[i][0])))
        #     for j in range(i+1, length):
        #         if trace[j][1]==103:
        #             cons.append(Implies((Int("pc_"+str(trace[i][0]))<Int("pc_"+str(trace[j][0]))),
        #                                         (Int("pt_"+str(trace[i][0]))<=Int("pc_"+str(trace[j][0])))
        #                                         ))
        #Now encoding the lock semantics:
        if trace[i][1]==105:
            lock = trace[i][0]
            unlock = "UnLock_"+str(trace[i][0]).split("_")[1]
            for j in range(0, length):
                if trace[j][-2]!=trace[i][-2]:
                    cons.append(Or(Int("interleave_"+str(trace[j][0]))<Int("pc_"+lock), 
                                   Int("interleave_"+str(trace[j][0]))>Int("pc_"+unlock)))
                if trace[j][1]==105 or trace[j][1]==106:
                    #No lock or unlock should occur within a lock-unlock pair
                    cons.append(Or(Int("pc_"+str(trace[j][0]))<Int("pc_"+lock), 
                                   Int("pc_"+str(trace[j][0]))>Int("pc_"+unlock)))

        # Now, we generate blocking constraints:
        # 2. Search for all Store, Lock pairs
        # Begin from the two stores we care about. Look for all the sfences in their respective threads after them.
        # For all the sfence add blocking constraint of (Sfence, unlock)
        if trace[i][1]==101 and (trace[i][0]==t1[0] or trace[i][0]==t2[0]):
            for j in range(i+1, length):
                if trace[j][1]==103 and trace[i][-2]==trace[j][-2]:
                    if trace[j][-2]==t1[-2]:
                        blockingConstraints.append([trace[j][0], unlock_1[0]])
                    if trace[j][-2]==t2[-2]:
                        blockingConstraints.append([trace[j][0], unlock_2[0]])

    cons.append(Int("interleave_"+str(t1[0]))>Int("interleave_"+str(t2[0])))
    # print("Number of constraints generated: ", len(cons))
    # print("Priniting all lock constraints:")
    # for assertion in cons:
    #     if "lock" in str(assertion):
    #         print(assertion)
    print("Printing all blocking constraints:")
    for b in blockingConstraints:
        print(b)
    """
    What all needs to be encoded now?
    1. 0 < pc_i < lastStmt                          -------Done
    2. pc_i != pc_j ; if i!=j                       -------Done
    3. Persistent time begins at the time of STOREs -------Done
    4. Persistent time ends at the first FENCE      -------Done
    5. Lock semantics

    BE MINDFUL OF THE THREAD IDS.

    But, before building all constraints, 
    I first need to build constraints from 1-5 and check if the bug is already fixed.
    If the bug is already fixed, I should return.
    If the bug is not already fixed:
    1. Add lock-unlock statements in both threads.
    2. Fir the thread that reads: Simply add lock and unlock statements before and after the STORE, 
        i.e if Store(y) reads from Store(x):
        Add: 
            a. pc_Lock(mutex_r, t2)+1 = pc_Store(y)
            b. pc_Store(y)+1 = pc_UnLock(mutex_r, t2)
            c. pc_Lock(mutex_r, t1)+1 = pc_Store(x)
        Now, all we have to do is find the most apropriate position for pc_UnLock(mutex_r, t1)

    """
    #New ideas:
    """
    Ideas to include:
    1. Perform slicing on per bug basis. 
    Slice of each bug should only contain the two stores, all sfences after them and locks and unlocks.
    2. Recombination strategy for Slices repaired?
    3. Constraints for reading thread: 
        a. If store in reading thread is not in Locked Reads, add:
        b. pc_Lock(mutex_r, t2)+1 = pc_Store(y)
        c. pc_Store(y)+1 = pc_UnLock(mutex_r, t2)
    """

    # for i in len(trace):
    return repairedTrace, constraintsToReturn

def addConstraints(inputFileName):
    trace = parseTrace(inputFileName)
    repairedTrace = trace
    
    print("Completed parsing.")

    global lastStmt
    lastStmt = len(trace)
    
    print("Local variables initialized.")

    bugs = []
    length = len(trace)
    mpas = []

    for i in range(length):
        if trace[i][1]==101:
            for j in range(i+1, length):
                if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]!=trace[j][-2]:
                    if [str(trace[i][-1]), str(trace[j][-1])] not in mpas:
                        bugs.append(Int("pt_"+str(trace[i][0]))<Int("pt_"+str(trace[j][0])))
                        mpas.append([str(trace[i][-1]), str(trace[j][-1])])
    
    print("Number of bugs detected: ", len(bugs))
    for b in bugs:
        print(b)
    
    consAppend = []
    for bug in bugs:
        repairedTrace, consReturned = RepairSingleBug(repairedTrace, bug, consAppend)
        for c in consReturned:
            consAppend.append(c)
        break

    return repairedTrace, len(bugs)

if __name__ == "__main__":
    inputFileName = sys.argv[1]         # "trace-1.txt"
    outputFileName = sys.argv[2]

    t1 = time.time()
    step1_result, MPACount = addConstraints(inputFileName)
    timeTaken = time.time()-t1

    f = open(outputFileName, "w")
    for stmt in step1_result:
        f.write(str(stmt))
        f.write("\n")
    f.close()

    f = open("Report.txt", "a")
    f.write("###########################################################################\n")
    f.write("Number of MPAs fixed: "+str(MPACount)+"\n")
    f.write("Total time taken to repair MPA bugs: "+str(timeTaken)+" seconds.\n")
    f.write("###########################################################################\n\n")
    f.close()
