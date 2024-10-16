from z3 import *

"""
Just a collection of helper functions universally called.
"""

benchmarks = ["skipLists"]
# "Clevel_hashing" , "memcached", "CCEH",  "P-CLHT", "fastFair", "array", "doublyList", "dqueue", 
#                   "graph", "hash", "heap", "list_1", "list", "motivatingExample", 
#                   "priorityQueue", "queue_1", "queue_2", "queue", "set", "skipLists", 
#                   "stack", "stack_1"]

def printer(model, map):
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

def getIndividualThreads(trace, threadCountParam):
    threadCount = set()
    for t in trace:
        threadCount.add(t[-2])
    #Function to seperate out individual threads from one monolithic trace.
    indiThreads = []
    print("Thread IDs: ", len(threadCount))
    for i in list(threadCount):
        currentThread = []
        for j in range(len(trace)):
            # print(trace[j])
            if trace[j][-2]==i:
                currentThread.append(trace[j])
        indiThreads.append(currentThread)
        print("LENGTH OF THREAD: ", i, " : ", len(currentThread))

    return indiThreads

def getTransactionConstraints(trace):
    constraints = []
    for i in range(len(trace)):
        if trace[i][1]==201:
            stores = []
            for j in range(i, len(trace)):
                if trace[j][1]==202:
                    # One I get a commit message, I can add all constraints.
                    for store in stores:
                        constraints.append(store<Int("pc_"+str(trace[j][0])))
                    break
                stores.append(Int("pt_"+str(trace[j][0])))

    return constraints

def processTransactions(trace):
    traceToReturn = []
    lockCount = 1
    for i in range(len(trace)):
        if trace[i][1]==201:
            lock = ["Lock_t"+str(lockCount), 105, 'M2', -1, trace[i][-2], trace[i][-1]]
            traceToReturn.append(trace[i])
            traceToReturn.append(lock)

        elif trace[i][1]==202:
            unlock = ["UnLock_t"+str(lockCount), 106, 'M2', -1, trace[i][-2], trace[i][-1]]
            traceToReturn.append(unlock)
            traceToReturn.append(trace[i])
            lockCount += 1
       
        else:
            traceToReturn.append(trace[i])

    return traceToReturn

def readScopes(path):
    f = open(path)
    bugs = set()
    for line in f:
        if "DURA" in str(line):
            b = str(line).replace("DURA:[ pt_", "").split("_")[0:-1]
            bugs.add('_'.join(str(x) for x in b).strip())

        elif "MPB" in str(line):
            bug = str(line).replace("MPB: [pt_", "").replace("]", "").split(";")
            b1 = bug[0].split("_")[:-1]
            b2 = bug[1].split("_")[1:-1]
            bugs.add('_'.join(str(x) for x in b1).strip())
            bugs.add('_'.join(str(x) for x in b2).strip())

        elif "MPA" in str(line):
            bug = str(line).replace("MPA: [pc_", "").replace("]", "").split(";")
            b1 = bug[0].split("_")[:-1]
            b2 = bug[1].split("_")[1:-1]
            bugs.add('_'.join(str(x) for x in b1).strip())
            bugs.add('_'.join(str(x) for x in b2).strip())
        
    return bugs

def getRelevantTrace(trace, fileName):
    inputPath = "../results/bugs/" 
    bugs = list(readScopes(inputPath+fileName+"_1.txt"))
    bugs.extend(list(readScopes(inputPath+fileName+"_2.txt")))
    # for bug in set(bugs):
    #     print(bug)
    finalTrace = []
    for t in trace:
        lineDetails = t[-1].split("_")[:-1]
        scope = '_'.join(str(x) for x in lineDetails).strip()
        if scope in bugs:
            finalTrace.append(t)
    
    # for t in finalTrace:
    #     print(t)
    return finalTrace