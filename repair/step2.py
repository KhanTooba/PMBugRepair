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

def RepairSingleBug(trace, bug):
    repairedTrace = trace

    return repairedTrace

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
    
    for bug in bugs:
        repairedTrace = RepairSingleBug(repairedTrace, bug)
            
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
    f.write("Total time taken to repair DURA bugs: "+str(timeTaken)+" seconds.\n")
    f.write("###########################################################################\n\n")
    f.close()
