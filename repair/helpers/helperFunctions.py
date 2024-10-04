from z3 import *

"""
Just a collection of helper functions universally called.
"""

benchmarks = ["memcached", "CCEH", "array", "doublyList", "dqueue", "fastFair", 
                  "graph", "hash", "heap", "list_1", "list", "motivatingExample", 
                  "priorityQueue", "queue_1", "queue_2", "queue", "set", "skipLists", 
                  "stack", "stack_1", "P-CLHT"]

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

def getIndividualThreads(trace, num_threads):
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
