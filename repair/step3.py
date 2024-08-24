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
lockedWrites = []

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
    traceParsed.append(int(elements[3].strip()))
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

def RepairSingleBug(originalTrace, trace, bug, previousConstraints):
    global r
    global lockedReads
    global lockedWrites

    print("Length of trace fed: ", len(trace))
    repairedTrace = []
    for t in trace:
        repairedTrace.append(t)
    # z3.set_option(verbose=2)
    solver = Solver()
    constraintsToReturn = []
    mapStmts = {}
    blockingConstraints = [] #We want all pairs of {Store, Lock} and {Sfence, unlock}

    cons = []
    
    indiThreads = getIndividualThreads(originalTrace)
    for thread in indiThreads:
        for i in range(len(thread)-1): #Building basic constraints: There has to be a strict dependency between each statement.
            # Now we can not rearrange statements. Only the Lock statements can be floating
            cons.append(Int("pc_"+str(thread[i][0])) < Int("pc_"+str(thread[i+1][0])))
            # print(Int("pc_"+str(thread[i][0])) < Int("pc_"+str(thread[i+1][0])))
            # cons.append(Int("interleave_"+str(thread[i][0])) < Int("interleave_"+str(thread[i+1][0])))

    print("Number of basic constraints: ", len(cons))

    t1, t2 = 0, 0
    for t in trace:
        if "pt_"+str(t[0])==str(bug).split("<")[0].replace(" ", ""):
            t1 = t
        if "pt_"+str(t[0])==str(bug).split("<")[1].replace(" ", ""):
            t2 = t

    additionStmts = []
    lock_1, lock_2, unlock_1, unlock_2 = [], [], [], []  
    """
    4 conditions:
    Write is locked | Read is locked | Stmts to be added
            Y       |       Y        |    No repair needed. Simply return.
            Y       |       N        |    Just add lock for read and add constraints of lock+1=read; read+1=unlock
            N       |       Y        |    Add constraint that lock+1=write; seacrh for a position for unlock
            N       |       N        |    Add constraints of lock+1=read; read+1=unlock. Add constraint that lock+1=write; seacrh for a position for unlock.
    """
    if t1[0] in lockedWrites and t2[0] in lockedWrites: #condition 1
        print("No repair needed.")
        return constraintsToReturn, additionStmts, True
    
    elif t1[0] in lockedWrites and t2[0] not in lockedWrites: #condition 2
        print("Only adding locks on read. Will process.")
        lock_2 = ["Lock_"+str(r), 105, "M1", -1, t2[4], t2[5]]
        unlock_2 = ["UnLock_"+str(r), 106, "M1", -1, t2[4], t2[5]]
        cons.append(Int("pc_Lock_"+str(r)) < Int("pc_UnLock_"+str(r)))
        constraintsToReturn.append(Int("pc_Lock_"+str(r))< Int("pc_UnLock_"+str(r)))
        r += 1
        # constraintsToReturn.append(Int("pc_"+str(lock_2[0]))+1==Int("pc_"+str(t2[0])))
        # constraintsToReturn.append(Int("pc_"+str(unlock_2[0]))==Int("pc_"+str(t2[0]))+1)
        trace.append(lock_1)
        trace.append(unlock_1)

        additionStmts.append(lock_2)
        additionStmts.append(unlock_2)
        lockedWrites.append(t2[0])
    
    elif t1[0] not in lockedWrites and t2[0] in lockedWrites: #condition 3
        print("Adding lock only for write. Will process.")
        lock_1 = ["Lock_"+str(r), 105, "M1", -1, t1[4], t1[5]]
        unlock_1 = ["UnLock_"+str(r), 106, "M1", -1, t1[4], t1[5]]
        cons.append(Int("pc_Lock_"+str(r)) < Int("pc_UnLock_"+str(r)))
        constraintsToReturn.append(Int("pc_Lock_"+str(r)) < Int("pc_UnLock_"+str(r)))
        r += 1

        # cons.append(Int("pc_"+str(lock_1[0]))+1==Int("pc_"+str(t1[0])))
        # constraintsToReturn.append(Int("pc_"+str(lock_1[0]))+1==Int("pc_"+str(t1[0])))

        trace.append(lock_1)
        trace.append(unlock_1)
        additionStmts.append(lock_1)
        additionStmts.append(unlock_1)
        lockedWrites.append(t1[0])
    
    else:
        print("All sorts of additions needed.")
        lock_1 = ["Lock_"+str(r), 105, "M1", -1, t1[4], t1[5]]
        unlock_1 = ["UnLock_"+str(r), 106, "M1", -1, t1[4], t1[5]]
        cons.append(Int("pc_Lock_"+str(r))< Int("pc_UnLock_"+str(r)))
        constraintsToReturn.append(Int("pc_Lock_"+str(r))< Int("pc_UnLock_"+str(r)))
        r += 1

        lock_2 = ["Lock_"+str(r), 105, "M1", -1, t2[4], t2[5]]
        unlock_2 = ["UnLock_"+str(r), 106, "M1", -1, t2[4], t2[5]]
        cons.append(Int("pc_Lock_"+str(r))< Int("pc_UnLock_"+str(r)))
        constraintsToReturn.append(Int("pc_Lock_"+str(r))< Int("pc_UnLock_"+str(r)))
        r += 1

        trace.append(lock_1)
        trace.append(unlock_1)
        trace.append(lock_2)
        trace.append(unlock_2)
        additionStmts.append(lock_1)
        additionStmts.append(unlock_1)
        additionStmts.append(lock_2)
        additionStmts.append(unlock_2)

        # cons.append(Int("pc_"+str(lock_1[0]))+1==Int("pc_"+str(t1[0])))
        # constraintsToReturn.append(Int("pc_"+str(lock_1[0]))+1==Int("pc_"+str(t1[0])))
        
        # cons.append(Int("pc_"+str(lock_2[0]))+1==Int("pc_"+str(t2[0])))
        # cons.append(Int("pc_"+str(unlock_2[0]))==Int("pc_"+str(t2[0]))+1)
        # constraintsToReturn.append(Int("pc_"+str(lock_2[0]))+1==Int("pc_"+str(t2[0])))
        # constraintsToReturn.append(Int("pc_"+str(unlock_2[0]))==Int("pc_"+str(t2[0]))+1)
        
        lockedWrites.append(t1[0])
        lockedWrites.append(t2[0])

    length = len(trace)
    pcs = []
    firstFence = -1
    for i in range(length):
        if trace[i][1]==101 and trace[i][0]==t1[0]:
            for j in range(i+1, length):
                if trace[j][1]==103 and trace[i][-2]==trace[j][-2]:
                    if trace[j][-2]==t1[-2]:
                        firstFence = j
    #We now build the remaining constraints
    for i in range(length):
        mapStmts["pc_"+str(trace[i][0])] = trace[i]
        pcs.append(Int("pc_"+str(trace[i][0])))
        cons.append(Int("pc_"+str(trace[i][0]))>0)
        cons.append(Int("pc_"+str(trace[i][0]))<length+1) #(0 <= pc_i <= max_stmt)
        # cons.append(Int("interleave_"+str(trace[i][0]))>0)
        # cons.append(Int("interleave_"+str(trace[i][0]))<length+1)

        # for j in range(i+1, length):
        #     cons.append(Int("pc_"+str(trace[i][0]))!=Int("pc_"+str(trace[j][0]))) #(pc_i != pc_j ; if i!=j)
        #     # cons.append(Int("interleave_"+str(trace[i][0]))!=Int("interleave_"+str(trace[j][0])))
        
        if trace[i][1]==101: #Do this for all STORES
            if "pt_"+str(trace[i][0])==str(bug).split("<")[0].replace(" ", ""):
                cons.append(Int("pt_"+str(trace[i][0]))>=Int("pc_"+str(trace[i][0]))) #Persistent time begins at the time of STOREs
                for j in range(i+1, len(trace)):
                        if trace[j][1]==103 :
                            cons.append(Implies((Int("pc_"+str(trace[i][0]))<Int("pc_"+str(trace[j][0]))),
                                                (Int("pt_"+str(trace[i][0]))<=Int("pc_"+str(trace[j][0])))
                                                ))

        #Now encoding the lock semantics:
        if trace[i][1]==105:
            # if trace[i][-2]==t1[-2]:
            #     blockingConstraints.append([t1[0], trace[i][0]])
            #     blockingConstraints.append([trace[firstFence][0], 'UnLock_'+str(trace[i][0]).split("_")[1]])
            lock = trace[i][0]
            unlock = "UnLock_"+str(trace[i][0]).split("_")[1]
            for j in range(0, length):
                # if trace[j][-2]!=trace[i][-2]:
                #     cons.append(Or(Int("interleave_"+str(trace[j][0]))<Int("pc_"+lock), 
                #                    Int("interleave_"+str(trace[j][0]))>Int("pc_"+unlock)))
                if (trace[j][1]==105 and trace[j][0]!=lock) or (trace[j][1]==106 and trace[j][0]!=unlock) :
                    #No lock or unlock should occur within a lock-unlock pair
                    cons.append(Or(Int("pc_"+str(trace[j][0]))<Int("pc_"+lock), 
                                   Int("pc_"+str(trace[j][0]))>Int("pc_"+unlock)))

    cons.append(Distinct(pcs))

    bug_Cons = []
    bug_Cons.append(Int("pt_"+str(t1[0]))>Int("pc_"+str(t2[0])))
    cons.append(Int("pc_"+str(t1[0]))<Int("pc_"+str(t2[0])))
    # print(Int("pc_"+str(t1[0]))<Int("pc_"+str(t2[0])))
    print("Number of constraints generated: ", len(cons))
    print("Number of blocking constraints:", len(blockingConstraints))
    for b in blockingConstraints:
        print(b)
    
    solver.add(cons)
    solver.add(bug_Cons)
    solver.add(previousConstraints)

    s = Solver()
    s.add(cons)

    sais = []
    iter1 = 1

    while solver.check()==sat:
        print("\nITERATION: ", iter1)
        print("Num:", len(solver.assertions()))

        model = solver.model()
        
        sai = []
        #we want a blocking constraint between every (store, fence) pair
        for b in blockingConstraints:
            sai.append(constructConstraint(b[0], b[1], model))
        
        iter1 += 1
        solver.add(Not(And(sai)))
        # print(Not(And(sai)))
        sais.append(Not(And(sai)))

    else:
        print("Not running blocking constraint generation because already unsat.")

    saisToSend = simplify(And(sais))
    s.add(simplify(And(sais)))
    # print("SAIS:", simplify(And(sais)))
    constraintsToReturn.append(simplify(And(sais)))

    repairedTrace = trace

    if s.check()==sat:
        model = s.model()
        repairedTrace = printer(model, mapStmts)

    else:
        print("Repair not found.")

    # saiToSend = simplify(And(sais))
    
    return constraintsToReturn, additionStmts, saisToSend

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

def sliceForRecombination(trace, indexes):
    slice = []
    
    for i in range(len(trace)):
        if trace[i][1]==101 and "pt_"+str(trace[i][0]) in indexes:
            slice.append(trace[i])
        elif trace[i][1]!=101:
            slice.append(trace[i])
    
    return slice
       
def generateSlice(trace, bug):
    # print(trace)
    slice = []
    # print("Bug:", str(bug).split("<")[0].replace(" ", ""), str(bug).split("<")[1].replace(" ", ""))
    s1, s2, t1, t2 = -1, -1, -1, -1
    for i in range(len(trace)):
        if trace[i][1]==101 and "pt_"+str(trace[i][0])==str(bug).split("<")[0].replace(" ", ""):
            s1 = i
            t1 = trace[i][-2]
        if trace[i][1]==101 and "pt_"+str(trace[i][0])==str(bug).split("<")[1].replace(" ", ""):
            s2 = i
            t2 = trace[i][-2]

    appendOnlyLocks = -1

    for i in range(len(trace)):
        t = trace[i]
        if "pt_"+str(t[0])==str(bug).split("<")[0].replace(" ", ""):
            slice.append(t)
        elif "pt_"+str(t[0])==str(bug).split("<")[1].replace(" ", ""):
            slice.append(t)
            appendOnlyLocks = 1
        elif t[-2]==t2 and (t[1]==105 or t[1]==106):
            slice.append(t)
        elif t[-2]==t1 and (appendOnlyLocks==1 and (t[1]==105 or t[1]==106)) or (
                appendOnlyLocks!=1 and i>s1 and t[1]!=101):
                slice.append(t)
    
    return slice

def recombine(originalTrace, trace, constraints):
    mapStmts = {}
    solver = Solver()
    
    for i in range(len(originalTrace)-1): #Building basic constraints: There has to be a strict dependency between each statement.
            # Now we can not rearrange statements.
            solver.add(Int("pc_"+str(originalTrace[i][0])) < Int("pc_"+str(originalTrace[i+1][0])))

    length = len(trace)
    pcs = []
    for i in range(length):
        mapStmts["pc_"+str(trace[i][0])] = trace[i]
        pcs.append(Int("pc_"+str(trace[i][0])))
        solver.add(Int("pc_"+str(trace[i][0]))>0)
        solver.add(Int("pc_"+str(trace[i][0]))<length+1) #(0 <= pc_i <= max_stmt)
        
    solver.add(Distinct(pcs))
    # print(solver.assertions())
    lockCons = []
    for i in range(length):
        if trace[i][1]==105:
            lock = trace[i][0]
            unlock = "UnLock_"+str(trace[i][0]).split("_")[1]
            for j in range(0, length):
                if (trace[j][1]==105 and trace[j][0]!=lock) or (trace[j][1]==106 and trace[j][0]!=unlock) :
                    #No lock or unlock should occur within a lock-unlock pair
                    lockCons.append(Or(Int("pc_"+str(trace[j][0]))<Int("pc_"+lock), 
                                   Int("pc_"+str(trace[j][0]))>Int("pc_"+unlock)))

    print("Basic constraints added: ", len(solver.assertions()))
    
    solver.add(constraints)
    solver.add(lockCons)

    print("All added.")
    if solver.check()==sat:
        print("Recombined successfully.")
        model = solver.model()
        # print(model)
        repaired = printer(model, mapStmts)
        return repaired
    else:
        print("Couldn't recombine.")
        return trace

def getFullTrace(trace, repairedTrace):
    print(repairedTrace)
    traceToSend = []
    i, j = 0, 0
    maxLen = len(trace)

    while i<maxLen:
        stmtToFind = trace[i]
        traceToSend.append(stmtToFind)
        for k in range(j, len(repairedTrace)):
            if repairedTrace[k][0]==stmtToFind[0]:
                l = k+1
                while l<len(repairedTrace):
                    if "Lock" in str(repairedTrace[l][0]):
                        traceToSend.append(repairedTrace[l])
                        l += 1
                        j = l
                    else:
                        j = l
                        break
        i += 1

    return traceToSend

def addConstraints(inputFileName):
    firstOcc = {}
    trace = parseTrace(inputFileName)
    repairedTrace = parseTrace(inputFileName)
    for t in trace:
        if t[-1] not in firstOcc.keys():
            firstOcc[t[-1]] = t

    print("Completed parsing.")
    global lastStmt
    lastStmt = len(trace)
    print("Local variables initialized.")

    bugs = []
    length = len(trace)
    mpas = []
    i = 0
    rename = {}
    allBugIndexes = []

    while i<length:
        if trace[i][1]==101:
            for j in range(i+1, length):
                if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]!=trace[j][-2] and not(trace[i][-1]==140 or trace[i][-1]==141):
                    if [str(trace[i][-1]), str(trace[j][-1])] not in mpas:
                        bugs.append(Int("pt_"+str(trace[i][0]))<Int("pt_"+str(trace[j][0])))
                        # bugs.append(Int("pt_"+str(firstOcc[trace[i][-1]][0]))<Int("pt_"+str(firstOcc[trace[j][-1]][0])))
                        # print("Appending: ", Int("pt_"+str(trace[i][0]))<Int("pt_"+str(trace[j][0])))
                        mpas.append([str(trace[i][-1]), str(trace[j][-1])])
                        allBugIndexes.append(trace[i][0])
                        allBugIndexes.append(trace[j][0])
        i+= 1

    i = 0
   
    while i<length:
        if trace[i][0] in allBugIndexes:
            fencesLeft = -1
            # print("Starting: ", trace[i][0])
            for j in range(i+1, length):
                if trace[j][1]==103:
                    fencesLeft = 1
            
            if fencesLeft == -1:
                rename[trace[i][0]] = trace[i][0]
                i += 1
                continue

            for j in range(i+1, length):
                if trace[j][1]==103:
                    # print("Breaking at: ", trace[j][0])
                    i = j
                    break 
                if trace[j][1]==101 and trace[j][0] in allBugIndexes:
                    rename[trace[j][0]] = trace[i][0]
            # rename[trace[j][0]] = trace[i][0]
        i+= 1
    """
    # Using first occurence technique
    while i<length:
        if trace[i][1]==101:
            for j in range(i+1, length):
                if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]!=trace[j][-2] and not(trace[i][-1]==140 or trace[i][-1]==141):
                    if [str(trace[i][-1]), str(trace[j][-1])] not in mpas:
                        # bugs.append(Int("pt_"+str(trace[i][0]))<Int("pt_"+str(trace[j][0])))
                        bugs.append(Int("pt_"+str(firstOcc[trace[i][-1]][0]))<Int("pt_"+str(firstOcc[trace[j][-1]][0])))
                        print("Appending: ", Int("pt_"+str(trace[i][0]))<Int("pt_"+str(trace[j][0])))
                        mpas.append([str(trace[i][-1]), str(trace[j][-1])])
                        allBugIndexes.append(firstOcc[trace[i][-1]][0])
                        allBugIndexes.append(firstOcc[trace[j][-1]][0])
        i+= 1
    
    i = 0
    while i<length:
        if firstOcc[trace[i][-1]][0] in allBugIndexes:
            print("Starting: ", firstOcc[trace[i][-1]][0])
            for j in range(i+1, length):
                if trace[j][1]==103:
                    print("Breaking at: ", firstOcc[trace[j][-1]][0])
                    i = j
                    break 
                if trace[j][1]==101 and firstOcc[trace[j][-1]][0] in allBugIndexes:
                    rename[firstOcc[trace[j][-1]][0]] = firstOcc[trace[i][-1]][0]
        i+= 1
    """
    
    newBugs = []
    for bug in bugs:
        first = int(str(bug).split("<")[0].replace("pt_", ""))
        second = int(str(bug).split("<")[1].replace("pt_", ""))
        renameFirst = first
        renameSecond = second
        if first in rename.keys():
            renameFirst = rename[first]
        if second in rename.keys():
            renameSecond = rename[second]

        newBugs.append(Int("pt_"+str(renameFirst))<Int("pt_"+str(renameSecond)))
        # print(Int("pt_"+str(renameFirst))<Int("pt_"+str(renameSecond)))

    print("Renames:", rename)
    bugs = newBugs
    print("Number of bugs detected: ", len(bugs))
    for b in bugs:
        print(b)
    
    consAppend = []
    indexes = []
    sais = []
    i = 1
    bcount = 0

    for bug in bugs:
        # if i>=7:
        #     break
        if str(bug).split("<")[0].replace(" ", "") not in indexes:
            indexes.append(str(bug).split("<")[0].replace(" ", ""))
        if str(bug).split("<")[1].replace(" ", "") not in indexes:
            indexes.append(str(bug).split("<")[1].replace(" ", ""))
        print("\n################################################################################################")
        print("Bug number: ", i)
        i += 1
        print("Repairing bug: ", bug)
        t1 = time.time()
        slicedOriginalTrace = generateSlice(trace, bug)
        slicedAppendedTrace = generateSlice(repairedTrace, bug)
        consReturned, stmtsToAppend, saisRecvd = RepairSingleBug(slicedOriginalTrace, 
                                                      slicedAppendedTrace, 
                                                      bug, consAppend)
        sais.append(saisRecvd)
        for c in consReturned:
            consAppend.append(c)
        for stmt in stmtsToAppend:
            repairedTrace.append(stmt)
        t2 = time.time()
        print("Time taken: ", (t2-t1), " seconds.")
        # repairedTrace = recombine(trace, repairedTrace, consAppend)
        print("################################################################################################")

    for s in sais:
        consAppend.append(s)
    # originalTraceRecombine = sliceForRecombination(trace, indexes)
    # repairedTraceRecombine = sliceForRecombination(repairedTrace, indexes)
    # print("Len: ", len(trace))
    # print("Len: ", len(originalTraceRecombine))
    # print("Len: ", len(repairedTraceRecombine))
    # repairedTrace = recombine(originalTraceRecombine, repairedTraceRecombine, consAppend)

    # repairedTrace = getFullTrace(trace, repairedTrace)

    repairedTrace = recombine(trace, repairedTrace, consAppend)

    # repairedTrace = getFullTrace(trace, repairedTrace)

    # repairedTrace = recombine(trace, repairedTrace, consAppend)
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
    f.write("Adding Report for "+str(inputFileName)+": \n")
    f.write("Number of MPAs fixed: "+str(MPACount)+"\n")
    f.write("Total time taken to repair MPA bugs: "+str(timeTaken)+" seconds.\n")
    f.write("###########################################################################\n\n")
    f.close()
