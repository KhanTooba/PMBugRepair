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

    print("Returning from parceTrace.py")
    return trace, infoToSend

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

def repairDURA(thread, bug, previousConstraints):
    # Globals
    global claimedFlushes
    global num_fence
    global num_flush
    global num_solverCalls

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
            # print("pt_"+str(thread[i][0]),str(bug).split("<")[0].replace(" ", ""),  "pt_"+str(thread[i][0])!=str(bug).split("<")[0].replace(" ", ""))
            if "pt_"+str(thread[i][0])!=str(bug).split("<")[0].replace(" ", ""):
                continue
            else:
                print("Bug found: ", "pt_"+str(thread[i][0]), str(bug).split("<")[0].replace(" ", ""))
                bugFlag = 1
            for j in range(0, length): #Change this to run from 0 to length so that all clflushopts 
                # that already exist and might have been rearranged can be utilized instead of adding new ones
                if thread[j][1]==102 and thread[i][2]==thread[j][2] and not(thread[j][0] in claimedFlushes) and (
                    str(thread[i][-1]).split("_")[0]==str(thread[j][-1]).split("_")[0] or '_' not in str(thread[j][-1])):
                    # Ensure that the clflushopt is present in the same function as the STORE
                    
                    foundFlush = j
                    claimedFlushes.append(thread[j][0])
                    print("Constraint added:", Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[j][0]))-1)
                    solver.add(Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[j][0]))-1)
                    constraintsToReturn.append(Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[j][0]))-1)
                    break
            
            if "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", ""):
                # print(bug)
                if foundFlush==-1:
                    # print("Flush has not been found:", foundFlush)
                    flush = [str(thread[i][0])+"_"+str(r), 102, thread[i][2], -1, thread[i][4], str(thread[i][5])+"_x"]
                    num_flush += 1
                    print("Adding:", flush)
                    r += 1
                    thread.insert(i+1, flush)
                    cons = Int("pc_"+str(thread[i][0]))==Int("pc_"+str(thread[i+1][0]))-1
                    claimedFlushes.append(thread[i+1][0])
                    solver.add(cons)
                    constraintsToReturn.append(cons)
                    print("Constraint added:", cons)
                    # bugFlag = 1
            
            for j in range(i+1, length):
                if thread[j][1]==103: # and str(thread[i][-1]).split("_")[0]==str(thread[j][-1]).split("_")[0]: 
                    # For DURA: Fence being in the same function is not important. Scope is relevant only for CLFLUSHOPT()
                    foundFence = 1 
            # print("pt_"+str(thread[i][0]))
            
            if "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", ""):
                if foundFence==-1:
                    # print("Fence has not been found.")
                    fence = [str(thread[i][0])+"_"+str(r), 103, '0', -1, thread[i][4], str(thread[i][5])+"_x"]
                    num_fence += 1
                    print("Adding:", fence)
                    # print(thread[i])
                    r += 1
                    thread.append(fence)
                    # bugFlag = 1
    
    return thread, constraintsToReturn, bugFlag

def repairMPB(thread, bug, previousConstraints):
    global num_solverCalls

    solver = Solver()
    map = {}
    blocking = []
    constraintsToReturn = []
    global r
    global num_fence

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
                            print("Fence found.", thread[k][0])
                            countFence += 1
                            # blocking.append([thread[i][0], thread[k][0]])
                    print("Fence count:", countFence)
                    if countFence<2:
                        fence = [str(thread[i][0])+"_Fence_"+str(r), 103, '0', -1, thread[i][4], str(thread[i][5])+"_x"]
                        num_fence += 1
                        r += 1
                        thread.append(fence)
                    break
    
    length = len(thread)
    print("After append:", length)
    print("The bug flag is:", bugFlag)
    pcs = []
    for i in range(length):
        pcs.append(Int("pc_"+str(thread[i][0])))

        map["pc_"+str(thread[i][0])] = thread[i]
        solver.add(Int("pc_"+str(thread[i][0]))>0, Int("pc_"+str(thread[i][0]))<length+1) #(0 <= pc_i <= max_stmt)
        
        # for j in range(i+1, length):
        #     solver.add(Int("pc_"+str(thread[i][0]))!=Int("pc_"+str(thread[j][0]))) #(pc_i != pc_j ; if i!=j)

        if thread[i][1]==101: #Do this for all STORES
            for j in range(i+1, length):
                if thread[j][1]==101:
                    solver.add(Int("pc_"+str(thread[i][0]))<Int("pc_"+str(thread[j][0]))) #All STOREs must follow their original order
                    break
            
            solver.add(Int("pt_"+str(thread[i][0]))>=Int("pc_"+str(thread[i][0]))) #Persistent time begins at the time of STOREs
            
            #This relates to the MPB bugs
            # print(bug, thread[i])
            if not(thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", "")) and not(
                thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[1].replace(" ", "")): 
                continue
            #How do I construct blocking constraints for MPB Bugs
            print("Did not continue for:", thread[i][0])
            if (thread[i][1]==101 and "pt_"+str(thread[i][0])==str(bug).split("<")[0].replace(" ", "")): 
                for j in range(i+1, len(thread)):
                    if (thread[j][1]==101 and "pt_"+str(thread[j][0])==str(bug).split("<")[1].replace(" ", "")):
                #Checking if the store is a part of the MPB Bug
                #If the store is a part of the MPB Bug, then we need to keep all the fences after it in the blocking constraint
                        for k in range(j+1, len(thread)):
                            if thread[k][1]==103:
                                blocking.append([thread[i][0], thread[k][0]])
                                blocking.append([thread[j][0], thread[k][0]])
            
            for j in range(i+1, len(thread)):
                    if thread[j][1]==103 :
                        if "pt_"+str(thread[i][0]) in str(bug):
                            solver.add(Implies((Int("pc_"+str(thread[i][0]))<Int("pc_"+str(thread[j][0]))),
                                                (Int("pt_"+str(thread[i][0]))<=Int("pc_"+str(thread[j][0])))
                                                ))

    print("The number of assertions:", len(solver.assertions()))
    print("The number of blocking constraint will be: ", len(blocking))
    print("Blocking constraints:", blocking)
    
    s = Solver()
    solver.add(previousConstraints)
    solver.add(Distinct(pcs))
    # print(Distinct(pcs))

    for assertion in solver.assertions():
        s.add(assertion)
        # print(assertion)

    solver.add(Not(bug))
    
    # print("Previous constraints:", previousConstraints)

    print("Bug is:", Not(bug))

    iter1 = 1
    
    sais = []
    while solver.check()==sat:
        num_solverCalls += 1
        print("Num:", len(solver.assertions()))
        model = solver.model()
        
        sai = []
        #we want a blocking constraint between every (store, fence) pair
        for b in blocking:
            sai.append(constructConstraint(b[0], b[1], model))
        
        print("ITERATION: ", iter1)

        iter1 += 1
        solver.add(Not(And(sai)))
        print(Not(And(sai)))
        sais.append(Not(And(sai)))
        """
        Why are the sai constraints not adding up? 
        Why not giving me a different solution?
        """

    else:
        num_solverCalls += 1
        print("Not running blocking constraint generation because already unsat.")

        #(STORE(&x)->CLFLUSHOPT(&x))->.........->SFENCE()
    s.add(simplify(And(sais)))
    print("SAIS:", simplify(And(sais)))
    constraintsToReturn.append(simplify(And(sais)))

    repairedThread = thread

    if s.check()==sat:
        model = s.model()
        repairedThread = printer(model, map, thread)

    else:
        print("Repair not found.")
        return repairedThread, constraintsToReturn, -1
    
    return repairedThread, constraintsToReturn, 1
    
def repairThread(thread, bugs):
    global fixedBugs
    """
    Plan:
    1. List out all the bugs----Done in previous function
    2. For each bug:
        a. Create a solver. ----Done for DURA
        b. Solve it.        ----Done for DURA
    """
    cons = []
    timeDura = 0
    timeMPB = 0
    for b in bugs:
        # if b in fixedBugs:
        #     continue
        print("Repairing for bug:", b)
        if str(inf) in str(b): # and "pt_70" in str(b):
            t1 = time.time()
            thread, cons_1, success = repairDURA(thread, b, cons)
            if success==1:
                bugs.remove(b)
                print("Removing:", b)
            timeDura += time.time()-t1
            for constraint in cons_1:
                cons.append(constraint)

        else:
            print("MPB Bug found:", b)
            t1 = time.time()
            thread, cons_1, success = repairMPB(thread, b, cons)
            if success==1:
                print("Removing:", b)
                bugs.remove(b)
            timeMPB += time.time()-t1
            for constraint in cons_1:
                cons.append(constraint)
        # print(thread)
        print("####################################################################################")
        fixedBugs.append(b)

    return thread, timeDura, timeMPB, bugs

def addConstraints(inputFileName, name):
    trace, threadInfo = parseTrace(inputFileName)
    
    store = 0
    for t in trace:
        if t[1]==101:
            store += 1
    print("Completed parsing.")
    global lastStmt
    lastStmt = len(trace)
    
    # lastStmt = trace[-1][0]
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
    timeDura, timeMPB = 0, 0
    store = 0

    bugs, totalMPB, totalDURA, failedMPB, failedDURA = readBugs("../results/bugs/"+str(name)+"_1.txt", trace, 9999)

    # for i in range(length):
    #     # print(trace[i])
    #     if trace[i][1]==101:
    #         if str(trace[i][-1]) not in duras:
    #             bugs.append(Int("pt_"+str(trace[i][0]))<inf)
    #             duras.append(str(trace[i][-1]))
            
    #         for j in range(i+1, length):
    #             if trace[j][1]==101 and trace[i][2]==trace[j][3] and trace[i][-2]==trace[j][-2]:
    #                 if str(trace[i][-1]) not in mpbs:
    #                     first = "pt_"+str(trace[i][0])
    #                     second = "pt_"+str(trace[j][0])
    #                     bugs.append(Int(first)<Int(second))
    #                     mpbs.append(str(trace[i][-1]))
    #                     break

    print("Number of bugs detected: ", len(bugs))
    for b in bugs:
        print(b)
    
    #We have all the unique bugs now
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
        threadreturned, t1, t2, bugs = repairThread(indiThreads[i], bugs)
        repaired_threads.append(threadreturned)
        timeDura += t1
        timeMPB += t2
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
        
    time3 = time.time()
    print("Time taken to recombine individual threads: ", (time3-time2), " seconds.")
    return recombinedTrace, len(duras), len(mpbs), threadInfo, timeDura, timeMPB, totalMPB, totalDURA, failedMPB, failedDURA

if __name__ == "__main__":
    inputFileName = sys.argv[1]         # "trace-1.txt"
    outputFileName = sys.argv[2]
    fileName = sys.argv[3]

    time1 = time.time()
    step1_result, duraCount, mpbCount, threadInfo, timeDURA, timeMPB, totalMPB, totalDURA, failedMPB, failedDURA = addConstraints(inputFileName, fileName)
    timeTaken = time.time()-time1

    f = open(outputFileName, "w")
    f.write(str(threadInfo))
    for stmt in step1_result:
        f.write(str(stmt[1:]))
        f.write("\n")
    f.close()

    f = open("Report.txt", "a")
    f.write("###########################################################################\n")
    f.write("Adding DURA & MPB Repair Report for "+str(fileName)+": \n")
    f.write("Number of DURAS fixed: "+str(totalDURA)+"\n")
    f.write("Number of MPBs fixed: "+str(totalMPB)+"\n")
    f.write("Number of DURAS failed to fix: "+str(failedDURA)+"\n")
    f.write("Number of MPBs failed to fix: "+str(failedMPB)+"\n")
    f.write("Total time taken to repair DURA bugs: "+str(timeDURA)+" seconds.\n")
    f.write("Total time taken to repair MPB bugs: "+str(timeMPB)+" seconds.\n")
    f.write("Number of sfences() added: "+str(num_fence)+"\n")
    f.write("Number of clflushopts() added: "+str(num_flush)+"\n")
    f.write("Total number of calls to the Z3 solver: "+str(num_solverCalls)+"\n")
    f.write("Total time taken: "+str(timeTaken)+" seconds.\n")
    f.write("###########################################################################\n\n")
    f.close()

"""
Time exceeding 4 hr limit. Optimizations:
1. Focusing on one bug at a time.
2. The clflushopt(&x) statement is fixed at the position right after STORE(&x).
3. 
"""
