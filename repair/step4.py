import time
from z3 import *
from helpers.readBugs import *
from helpers.helperFunctions import *

"""
Implementation of step 4 of the algorithm
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

def appendTraceWithLocks(trace, consToRepair, writes, reads, bugInfos):
    # Globals
    global r
    global lockedReads
    global lockedWrites
    global num_locks
    global num_fence

    repairedTrace = []
    bug = str(consToRepair).split("(")[1].split(",")[0]
    first = str(bug).split("<")[0].replace("pc_", "").replace(" ", "")
    second = str(bug).split("<")[1].replace("pc_", "").replace(" ", "")
    info = bugInfos[str(first)+"-"+str(second)]
    ind1, ind2 = 0, 1
    if int(first)>int(second):
        first, second = second, first
        ind1, ind2 = ind2, ind1

    commonLocked = -1
    currentLock = -1
    lockedRead = -1
    lockedWrite = -1
    transactFirst, transactSecond = -1, -1
    transact = -1
    # print(first, second)
    for i in range(len(trace)):
        # print(trace[i])
        if trace[i][1]==201:
            transact = i
        
        elif trace[i][1]==202:
            transact = -1

        elif trace[i][1]==105:
            currentLock = i
        
        elif trace[i][1]==106:
            currentLock = -1
        
        elif trace[i][0]==int(first) and transact!=-1:
            transactFirst = transact
        
        elif trace[i][0]==int(second) and transact!=-1:
            transactSecond = transact
            # break

        elif trace[i][0]==int(first) and currentLock!=-1:
            lockedWrite = currentLock
            # print(trace[i], first, currentLock)
        
        elif trace[i][0]==int(second) and currentLock!=-1:
            lockedRead = currentLock
            # print(trace[i], second, currentLock)
            # break
    print(lockedRead, lockedWrite)
    currentLock = -1
    for i in range(len(trace)):
        if trace[i][1]==105:
            currentLock = i

        if trace[i][0]==int(first):
            commonLocked = currentLock
        
        if trace[i][1]==106:
            currentLock = -1
        
        if trace[i][0]==int(second) and currentLock==commonLocked and commonLocked!=-1:
            print("We found a common lock")
            if int(first) in lockedReads:
                lockedReads.remove(int(first))
            if int(first) in lockedWrites:
                lockedWrites.remove(int(first))
            if int(second) in lockedReads:
                lockedReads.remove(int(second))
            if int(second) in lockedWrites:
                lockedWrites.remove(int(second))
            
            lock1 = trace[commonLocked]
            
            for j in range(commonLocked, len(trace)):
                if trace[j][1]==106:
                    print("Removing: ", trace[j])
                    trace.remove(trace[j])
                    break
            
            print("Removing: ", lock1)
            trace.remove(lock1)
            num_locks -= 1
            lockedRead = -1
            lockedWrite = -1
            break
   
    traceIndex = 0
    insertedUnlock = False
    # print(first, second, transactFirst, transactSecond)
    print("Prinitng stats: ",lockedWrite, lockedRead, reads, writes)
    if int(first) in writes and lockedWrite==-1:
        # Add lock and unlock statements before store and right after sfence of first
        print("Adding locks for write.", first)
        lockedWrites.append(int(first))
        lockedReads.append(int(first))
        lock = ["Lock_"+str(r), 105, "M1", -1, info[ind1][4], str(info[ind1][5])+"_x"]
        unlock = ["UnLock_"+str(r), 106, "M1", -1, info[ind1][4], str(info[ind1][5])+"_x"]
        fence = ["Fence_Lock_"+str(r), 103, 0, -1, info[ind1][4], str(info[ind1][5])+"_x"]
        r += 1

        foundfirst = -1
        i = traceIndex
        while i<len(trace)-1:
            if foundfirst==-1 and trace[i][0]!=int(first) and trace[i][0]!=int(second):
                repairedTrace.append(trace[i])
                i += 1

            elif trace[i][0]==int(first):
                print("Found insertion point for first lock: ", i, i+1, trace[i], lock)
                repairedTrace.append(lock)
                num_locks += 1
                repairedTrace.append(trace[i])
                foundfirst = i
                i += 1
            elif foundfirst!=-1 and (trace[i][-2]!=trace[foundfirst][-2]):
                print("Adding fence because another thread started.")
                repairedTrace.append(fence)
                num_fence += 1
                repairedTrace.append(unlock)
                print("Adding unlock:", unlock)
                insertedUnlock = True
                traceIndex = i
                break

            elif foundfirst!=-1 and (trace[i][0]==int(second) or trace[i][1]==105):
                print("Adding fence because encountered second before fence.")
                repairedTrace.append(fence)
                num_fence += 1
                repairedTrace.append(unlock)
                print("Adding unlock:", unlock)
                insertedUnlock = True
                traceIndex = i
                break

            elif foundfirst!=-1 and (trace[foundfirst][-1].split("_")[:-1]!=trace[i][-1].split("_")[:-1]):
                print("Adding fence because new scope started.")
                repairedTrace.append(fence)
                num_fence += 1
                repairedTrace.append(unlock)
                print("Adding unlock:", unlock)
                insertedUnlock = True
                traceIndex = i
                break

            elif foundfirst!=-1 and trace[i][1]==103 and trace[i][-2]==trace[foundfirst][-2]:
                repairedTrace.append(trace[i])
                repairedTrace.append(unlock)
                print("Adding unlock:", unlock)
                insertedUnlock = True
                traceIndex = i+1
                break
        
            

            else:
                if trace[i][1]==101 and (int(trace[i][0]) not in lockedWrites) and (
                    int(trace[i][0]) in writes or int(trace[i][0]) in reads
                    ) and foundfirst!=-1 and trace[i][-2]==trace[foundfirst][-2]:
                        lockedWrites.append(trace[i][0])
                        print("Locking ", trace[i])
                repairedTrace.append(trace[i])
                i += 1
        if not insertedUnlock:
            repairedTrace.append(fence)
            num_fence += 1
            print("Adding Unlock because no fence found throughout.")
            repairedTrace.append(unlock)
            insertedUnlock = True    
    elif int(first) not in writes and lockedWrite==-1:
        print("Adding very restricted lock for write.", first)
        lockedWrites.append(int(first))
        lock = ["Lock_"+str(r), 105, "M1", -1, info[ind1][4], str(info[ind1][5])+"_x"]
        unlock = ["UnLock_"+str(r), 106, "M1", -1, info[ind1][4], str(info[ind1][5])+"_x"]
        r += 1

        i = traceIndex
        while i<len(trace)-1:
            if trace[i][0]==int(first):
                repairedTrace.append(lock)
                repairedTrace.append(trace[i])
                num_locks += 1
                repairedTrace.append(unlock)
                repairedTrace.append(trace[i+1])
                
                traceIndex = i+2
                i += 2
                break
            else:
                repairedTrace.append(trace[i])
            i += 1
        while i<len(trace)-1:
            if trace[i][0]==int(second):
                traceIndex = i
                break
            else:
                repairedTrace.append(trace[i])
                i += 1
    
    insertedUnlock = False
    if int(second) in writes and lockedRead==-1:
        # Add lock and unlock statements before store and right after sfence of second
        print("Adding locks for read and taking fence within lock.", second)
        lockedWrites.append(int(second))
        lockedReads.append(int(second))
        lock = ["Lock_"+str(r), 105, "M1", -1, info[ind2][4], str(info[ind2][5])+"_x"]
        unlock = ["UnLock_"+str(r), 106, "M1", -1, info[ind2][4], str(info[ind2][5])+"_x"]
        fence = ["Fence_Lock_"+str(r), 103, 0, -1, info[ind2][4], str(info[ind2][5])+"_x"]
        r += 1
    
        foundSecond = -1
        i = traceIndex
        while i<len(trace):
            if foundSecond==-1 and trace[i][0]!=int(second):
                repairedTrace.append(trace[i])
                i+=1
                traceIndex = i

            if trace[i][0]==int(second):
                print("Found insertion point for second lock: ", i)
                repairedTrace.append(lock)
                num_locks += 1
                repairedTrace.append(trace[i])
                foundSecond = i
                i += 1

            elif foundSecond!=-1 and (trace[i][-2]!=trace[foundSecond][-2]):
                print("Adding fence because another thread started.")
                repairedTrace.append(fence)
                num_fence += 1
                repairedTrace.append(unlock)
                insertedUnlock = True
                traceIndex = i
                break
            
            elif foundSecond!=-1 and ((trace[i][0]==int(first) or trace[i][1]==105) or (
                trace[i][1]==103 and trace[i][-2]!=trace[foundSecond][-2])):
                print("Adding fence because encountered second before fence.")
                repairedTrace.append(fence)
                num_fence += 1
                repairedTrace.append(unlock)
                insertedUnlock = True
                traceIndex = i
                break
            
            elif foundSecond!=-1 and (trace[foundSecond][-1].split("_")[:-1]!=trace[i][-1].split("_")[:-1]):
                print("Adding fence because new scope started.")
                repairedTrace.append(fence)
                num_fence += 1
                repairedTrace.append(unlock)
                insertedUnlock = True
                traceIndex = i
                break

            # elif foundfirst!=-1 and (trace[foundfirst][-1].split("_")[:-1]!=trace[i][-1].split("_")[:-1]):

            elif foundSecond!=-1 and trace[i][1]==103 and trace[i][-2]==trace[foundSecond][-2]:
                print("Found fence at ", trace[i])
                repairedTrace.append(trace[i])
                repairedTrace.append(unlock)
                insertedUnlock = True
                traceIndex = i+1
                break

            else:
                if trace[i][1]==101 and (int(trace[i][0]) not in lockedWrites) and (int(trace[i][0]) in writes) and foundSecond!=-1:
                    lockedWrites.append(trace[i][0])
                repairedTrace.append(trace[i])
                i += 1
        if not insertedUnlock:
            repairedTrace.append(fence)
            num_fence += 1
            print("Adding Unlock because couldnt find termination point.")
            repairedTrace.append(unlock)
            insertedUnlock = True
    elif (int(second) not in writes) and lockedRead==-1:
        # Add lock and unlock statements before store and right after store of second
        print("Adding very restricted lock for read.", second)
        lockedReads.append(int(second))
        lock = ["Lock_"+str(r), 105, "M1", -1, info[ind2][4], str(info[ind2][5])+"_x"]
        unlock = ["UnLock_"+str(r), 106, "M1", -1, info[ind2][4], str(info[ind2][5])+"_x"]
        r += 1

        i = traceIndex
        while i<len(trace)-1:
            if trace[i][0]==int(second):
                # print("Found insertion point for second lock: ", i, trace[i][0])
                repairedTrace.append(lock)
                repairedTrace.append(trace[i])
                # print(num_locks)
                num_locks += 1
                repairedTrace.append(unlock)
                repairedTrace.append(trace[i+1])
                traceIndex = i+2
                i += 2
                break
            else:
                repairedTrace.append(trace[i])
            i += 1
   
    for i in range(traceIndex, len(trace)):
        if trace[i] not in repairedTrace:
            repairedTrace.append(trace[i])
        
    return repairedTrace

def addLocks(trace, reads, writes, transactCons, bugCons, bugInfos):
    global num_solverCalls 
    """
    Construct a constraint which says bug = give a trace in which atmost one of the constraint is satisfied.
    Then find out which constraint is satisfied.
    """
    cons = []
    pcs = []
    # print(reads, writes)
    
    openLock = -1
    for i in range(len(trace)-1):
        if trace[i][1]==105:
            openLock = i
        elif trace[i][1]==106:
            cons.append(Int("pc_"+str(trace[i-1][0])) < Int("pc_"+str(trace[i][0])))
            openLock = -1
        elif openLock!=-1:
            cons.append(Int("pc_"+str(trace[i-1][0])) < Int("pc_"+str(trace[i][0])))
    
    # print(cons)
    thread_counts = set()
    for t in trace:
        thread_counts.add(t[-2])
    # print(len(thread_counts), thread_counts)
    indiThreads = getIndividualThreads(trace, thread_counts)
    for thread in indiThreads:
        # print(thread)
        for i in range(len(thread)-1): #Building basic constraints: There has to be a strict dependency between each statement.
            # Now we can not rearrange statements. Only the Lock statements can be floating
            cons.append(Int("pc_"+str(thread[i][0])) < Int("pc_"+str(thread[i+1][0])))
    
    # print(cons)
    print("Ranges:", 0, len(trace)+1)
    for i in range(len(trace)):
        pcs.append(Int("pc_"+str(trace[i][0])))
        cons.append(Int("pc_"+str(trace[i][0]))>0)
        cons.append(Int("pc_"+str(trace[i][0]))<len(trace)+1) #(0 <= pc_i <= max_stmt)
        # for j in range(i+1, len(trace)):
        #     cons.append(Int("pc_"+str(trace[i][0]))!=Int("pc_"+str(trace[j][0]))) #(pc_i != pc_j ; if i!=j)
  

        if trace[i][1]==101: #Do this for all STORES
                cons.append(Int("pt_"+str(trace[i][0]))>=Int("pc_"+str(trace[i][0]))) 
                # print(Int("pt_"+str(trace[i][0]))>=Int("pc_"+str(trace[i][0]))) 
                # Persistent time begins at the time of STOREs
                for j in range(i+1, len(trace)):
                        if trace[j][1]==103 and trace[j][-2]==trace[i][-2]:
                            cons.append(Int("pt_"+str(trace[i][0]))<=Int("pc_"+str(trace[j][0])))
                            # print(Int("pt_"+str(trace[i][0]))<=Int("pc_"+str(trace[j][0])))
                            break
        # else:
        #     print(i, trace[i])
        if trace[i][1]==105:
            lock = trace[i][0]
            unlock = "UnLock_"+str(trace[i][0]).split("_")[1]
            cons.append(Int("pc_"+lock)<Int("pc_"+unlock))
            for j in range(0, len(trace)): # No lock or unlock should occur within a lock-unlock pair
                if (trace[j][1]==105 and trace[j][0]!=lock): # or (trace[j][1]==106 and trace[j][0]!=unlock) :
                    tobelocked = trace[j][0]
                    tobeunlocked = "UnLock_"+str(trace[j][0]).split("_")[1]
                    c1 = And(Int("pc_"+tobelocked)<Int("pc_"+lock), 
                            Int("pc_"+tobeunlocked)<Int("pc_"+lock))
                    c2 = And(Int("pc_"+tobelocked)>Int("pc_"+unlock), 
                             Int("pc_"+tobeunlocked)>Int("pc_"+unlock))
                    cons.append(Or(c1, c2))
                    # print(Or(c1, c2))
                    # cons.append(Or(Int("pc_"+str(trace[j][0]))<Int("pc_"+lock), 
                    #                Int("pc_"+str(trace[j][0]))>Int("pc_"+unlock)))
                    # print(Or(Int("pc_"+str(trace[j][0]))<Int("pc_"+lock), 
                    #                Int("pc_"+str(trace[j][0]))>Int("pc_"+unlock)))

    # cons.append(Distinct(pcs))
    print("Values to be assigned in that range:", len(pcs))
    print("Completed building constraints.\nNumber of constraints: ", len(cons))
    
    solver = Solver()
    # solver.set("timeout", 100000)
    
    solver.add(transactCons)
    solver.add(cons)
    solver.add(Or(bugCons))

    if solver.check()==sat:
        model = solver.model()
        num_solverCalls += 1
        print("A violation is found. Let us see which bug was being violated in this trace.")
        model = solver.model()
        for constraint in bugCons:
            truth_value = model.eval(constraint, model_completion=True)
            if truth_value==True:
                consToRepair = constraint
                print("Now, we will repair: ", consToRepair)
                trace = appendTraceWithLocks(trace, consToRepair, writes, reads, bugInfos)
                return trace, bugCons, True
    
    else:
        num_solverCalls += 1
        print("Model was unsat. This means all bugs have been repaired.")
        # print_UNSATCORE(solver)

    return trace, bugCons, False

def removeDeadlocks(trace):
    global num_locks
    traceRepaired = []
    toRemove = []
    openLock = -1
    for i in range(len(trace)):
        if trace[i][1]==105 and openLock==-1:
            openLock = i
            traceRepaired.append(trace[i])

        elif trace[i][1]==106 and openLock!=-1 and str(trace[i][0])=='Un'+str(trace[openLock][0]):
            openLock = -1
            traceRepaired.append(trace[i])

        elif trace[i][1]!=105 and trace[i][1]!=106:
            traceRepaired.append(trace[i])
        else:
            toRemove.append("Lock_"+str(trace[i][0]).split("_")[1])
            print("Removing  ", trace[i], "  for  ", trace[openLock])
            num_locks -= 1


    return traceRepaired , toRemove

def generateRepair(inputFileName, name):
    trace = parseTrace(inputFileName)
    transactCons = getTransactionConstraints(trace)
    # trace = processTransactions(trace)
    global lastStmt
    global num_threads
    lastStmt = len(trace)
    bugInfos = {}

    firstOcc = {}
    for t in trace:
        if t[-1] not in firstOcc.keys():
            firstOcc[t[-1]] = t
    
    reads, writes = [], []
    bugCount = 0
    bugCons = []
    i = 0

    print("Local variables initialized.")

    bugCons, totalMPA, failedMPA, bugInfos, writes, reads = readMPAs("../results/bugs/"+name+"_2.txt", trace) #/Users/toobakhan/Downloads/PMBugRepair/results/bugs/array_2.txt
    reads = list(set(reads) - set(writes)) 
    tid = num_threads+1
    #Let us fix the thread IDs 
    # for b in bugInfos:
    #     first, second = int(b.split("-")[0]), int(b.split("-")[1])
    #     for i in range(len(trace)):
    #         if trace[i][0]==first:
    #             for j in range(i, len(trace)):
    #                 trace[j][-2] = tid
    #                 if trace[j][1]==103:
    #                     tid += 1
    #                     break
                
    #         if trace[i][0]==second:
    #             for j in range(i, len(trace)):
    #                 trace[j][-2] = tid
    #                 if trace[j][1]==103:
    #                     tid += 1
    #                     break
    
    num_threads = tid
    bugCount = len(bugCons)
    print("Number of bugs to be repaired: ", bugCount)
    
    for b in bugCons:
        print(b)
    truthValue = True
    iterCount = 0
    print(set(reads), set(writes))
    
    setSize = max(1, len(bugCons))
    print("Set Size: ", setSize)
    for i in range(0, len(bugCons), setSize):
        start = i
        end = len(bugCons) if i+setSize>=len(bugCons) else i+setSize
        set1 = bugCons[start:end]
        print(len(set1), set1)
        truthValue = True
        while truthValue==True:
            print("\n############################################################################")
            t1 =  time.time()
            print("Iteration: ", iterCount+1)
            
            trace, set1, truthValue = addLocks(trace, reads, writes, transactCons, set1, bugInfos)
            trace, toRemove = removeDeadlocks(trace)
            indices = []
            for t in trace:
                if t[0] in indices:
                    print("Found duplicacy at:", t[0])
                indices.append(t[0])
            
            iterCount += 1
            # print(trace)
            t2 = time.time()
            # print(trace)
            print("Time taken: ", (t2-t1), " seconds.")
            print("\n############################################################################")

    print("\nTotal number of iterations: ", iterCount)
    return trace, bugCount, totalMPA, failedMPA

if __name__ == "__main__":
    inputFileName = sys.argv[1]         # "trace-1.txt"
    outputFileName = sys.argv[2]
    fileName = sys.argv[3]

    t1 = time.time()
    step1_result, MPACount, totalMPA, failedMPA = generateRepair(inputFileName, fileName)
    timeTaken = time.time()-t1

    f = open(outputFileName, "w")
    for stmt in step1_result:
        f.write(str(stmt))
        f.write("\n")
    f.close()

    f = open("Report.txt", "a")
    f.write("###########################################################################\n")
    f.write("Adding MPA Repair Report for "+str(fileName)+": \n")
    f.write("Number of MPAs fixed: "+str(MPACount)+"\n")
    f.write("Number of MPAs failed: "+str(failedMPA)+"\n")
    f.write("Number of fences() added: "+str(num_fence)+"\n")
    f.write("Number of locks() added: "+str(num_locks)+"\n")
    f.write("Total number of calls to the Z3 solver: "+str(num_solverCalls)+"\n")
    f.write("Total time taken to repair MPA bugs: "+str(timeTaken)+" seconds.\n")
    f.write("###########################################################################\n\n")
    f.close()
