import itertools
from z3 import *
import sys, os
from copy import copy

"""
Values for standard statements:
LOAD    100
STORE   101
CLFLUSH 102
SFENCE  103
LOCK 104
UNLOCK 105
"""
num_threads = 2
originalTraceLen = -1

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def printableSolver(solver):
    ref = {}
    model = solver.model()
    for m in model:
        if "pc" not in str(m):
            continue
        ref[int(str(model[m]))] = m
        
    sorted_ref = dict(sorted(ref.items()))
    # print(sorted_ref)
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
    if elements[0]=="'LOAD'":
        traceParsed.append(100)
    elif elements[0]=="'STORE'":
        traceParsed.append(101)
    elif elements[0]=="'FLUSH'":
        traceParsed.append(102)
    elif elements[0]=="'FENCE'":
        traceParsed.append(103)
    elif elements[0]=="'LOCK'":
        traceParsed.append(104)
    elif elements[0]=="'UNLOCK'":
        traceParsed.append(105)
    
    traceParsed.append(elements[1].strip().replace("'",""))
    traceParsed.append(elements[2].strip().replace("'",""))
    traceParsed.append(int(elements[3].strip()))
    traceParsed.append(int(elements[4].replace("'", "").strip()))
    
    return traceParsed

def parseTrace(file):
    """
    Trace is used in the following format: 
    1. Trace is a 2-D array
    2. Each element of the trace array is a line in the original trace file i.e a program statement
    3. trace[i][0] = element number in the trace 
    4. trace[i][1] = OPCODE (defined above)
    5. trace[i][2] = Target variable (Varible to be stored in case of STORE and FLUSH and a temporary variable in case of load)
    6. trace[i][3] = Value to be loaded (Value of importance in case of Loads)
    7. trace[i][4] = Thread ID
    8. trace[i][5] = statement/line number in original code
    """
    trace_file = open(file)
    trace = []
    counter = 1
    for line in trace_file:
        if "threads" in line:
            global num_threads
            num_threads = int(line.split(":")[1].strip())
            continue
        elements = line.strip("[]\n").split(",")
        trace.append(parseTraceHelper(elements, counter))
        counter += 1

    print("Thread count:", num_threads)
    return trace

def getAssertions(trace, fileName):
    # file = open(sys.argv[2]) #assertionsOPT.txt
    phi = []
    file = open(fileName)
    assertions = []

    # print("\nDurability constraints:")
    for line in file:
        if "DURA" in str(line):
            content = line.replace("]","").replace("\n","").split(":")[1]
            # add = content.split(",")[0]
            # line = content.split(",")[1]
            for t in trace:
                if str(t[2])==str(content) and t[1]==101:
                    d = Int("pt_"+str(t[0]))>=(len(trace)+1)
                    assertions.append(d)
                    # print(str(d)+"\n")

     #assertionsOPT.txt
    file.close()

    file = open(fileName)
    # print("\nPrinting crash consistency constraints:")
    for line in file:
        if "MPB" in str(line):
            add2 = line.replace("]","").replace("\n","").split("<")[1]
            add1 = line.split("<")[0].split(":")[1]
            
            s1, s2 = 0, 0
            for t in trace:
                if str(t[2])==str(add1) and t[1]==101:
                    s1 = t[0]
                if str(t[2])==str(add2) and t[1]==101:
                    s2 = t[0]
            
            c = Not(Int("pt_"+str(s1))<Int("pt_"+str(s2)))
            assertions.append(c)
            c = Int("pc_"+str(s1))<Int("pc_"+str(s2))
            phi.append(c)
            # print(str(c)+"\n")

    return assertions, phi

def appendTrace(trace):
    extra = []
    num = len(trace)+1
    global originalTraceLen
    originalTraceLen = len(trace)
    
    lockNum = 1
    for i in range(len(trace)):
        if trace[i][1]==101:
            found = -1
            for j in range(i+1, len(trace)):
                if trace[j][1]==102 and trace[j][2]==trace[i][2]:
                    found = 1
            if found==-1:
                extra.append([num, 102, trace[i][2], -1, trace[i][-2], -1 ])
                num += 1
                extra.append([num, 103, -1, -1, trace[i][-2], -1 ])
                num += 1
            
            extra.append([num, 104, lockNum, -1, trace[i][-2], -1 ])
            num += 1
            extra.append([num, 105, lockNum, -1, trace[i][-2], -1 ])
            num += 1
            lockNum += 1

    for e in extra:
        trace.append(e)

    return trace

def buildConstraints(trace):
    """
    This function builds all the constraints except the PM constraints 
    (which are retrieved from the assertion file).
    """
    pcs = []
    seq = []
    locks = []
    persist = []
    pt  = []

    N = len(trace)

    #Adding phi_pcs: to be built on modified trace
    for i in range(0, len(trace)):
        pcs.append(0<Int("pc_"+str(trace[i][0])))
        pcs.append(Int("pc_"+str(trace[i][0]))<=N)
        for j in range(len(trace)):
            if trace[j][0]!=trace[i][0]:
                pcs.append(Int("pc_"+str(trace[i][0]))!=Int("pc_"+str(trace[j][0])))

    #Adding phi_seq: to be built on original trace
    for t in range(0, num_threads):
        # print("For thread:", t)
        for i in range(len(trace)):
            if trace[i][1]==101 and trace[i][-2]==t:
                for j in range(i+1, len(trace)):
                    if trace[j][1]==101 and trace[j][-2]==t:
                        # print(trace[i], trace[j], t)
                        seq.append(Int("pc_"+str(trace[i][0]))<Int("pc_"+str(trace[j][0])))
    
    #Adding phi_lock: to be built on modified trace
    #Assumption: we insert only 1 lock and use only this lock for syncronization.
    for i in range(len(trace)):
        if trace[i][1]==104:
            lock = i
            unlock = -1
            for j in range(len(trace)):
                if trace[j][1]==105 and trace[i][2]==trace[j][2] and trace[i][-2]==trace[j][-2]:
                    #Found a lock-unlock pair
                    locks.append(Int("pc_"+str(trace[i][0]))<Int("pc_"+str(trace[j][0])))
                    unlock = j
                
            for j in range(len(trace)):
                if trace[j][1]==104 and j!=lock:
                    #Found a lock-unlock pair
                    locks.append(Or(Int("pc_"+str(trace[j][0]))<Int("pc_"+str(trace[lock][0])), #either the lock  in j happens before the lock
                                   Int("pc_"+str(trace[unlock][0]))<Int("pc_"+str(trace[j][0])))) # or it happens after the unlock
    """
    Thread 2 should lock on the 2nd variable. How will we know? No idea as of now!
    """
    #Adding phi_pt: to be built on original trace 
    originalTraceLen = len(trace)
    for i in range(originalTraceLen):
        if trace[i][1]==101: 
        #The persist timing interval for each store statment begins at that store and ends at a corresponding fence
            pt.append(Int("pt_"+str(trace[i][0]))<len(trace)+2)
            pt.append(Int("pt_"+str(trace[i][0]))>Int("pc_"+str(trace[i][0])))
            for j in range(i+1, originalTraceLen):
                if trace[j][1]==102 and trace[j][2]==trace[i][2]:
                    #Corresponding clflushopt found
                    for k in range(j+1, originalTraceLen):
                        if trace[k][1]==103:
                            #Corresponding sfence found
                            pt.append(Int("pt_"+str(trace[i][0]))<Int("pc_"+str(trace[k][0])))
            for j in range(0, originalTraceLen):
                if trace[j][1]==101 and j!=i:
                    pt.append(Int("pt_"+str(trace[i][0]))!=Int("pt_"+str(trace[j][0])))

    #Adding phi_persist
    for i in range(len(trace)):
        if trace[i][1]==102:
            # print("FLUSH", i)
            for j in range(0, i):
                if trace[j][1]==101 and trace[j][2]==trace[i][2] and trace[j][-2]==trace[i][-2]:
                    # print("STORE")
                    #CLFLUSHOPT cannot be encountered if a STORE hasn't been encountered
                    persist.append(Int("pc_"+str(trace[j][0]))<Int("pc_"+str(trace[i][0])))
                    # print(persist)
                    break

        if trace[i][1]==103:
            # print("FLUSH", i)
            for j in range(0, i):
                if trace[j][1]==102 and trace[j][-2]==trace[i][-2]:
                    # print("STORE")
                    #SFENCE() cannot be encountered if a CLFLUSHOPT() hasn't been encountered
                    persist.append(Int("pc_"+str(trace[j][0]))<Int("pc_"+str(trace[i][0])))
                    # print(persist)
                    break

    # print("Phi_PCs: ", pcs)
    # print("Phi_seq: ", seq)
    print("Phi_pts: ", pt)
    # print("Phi_lock:", locks)
    # print(persist)
    return pcs, seq, pt, persist, locks

def formatModel(model, trace):
    modelDict = {}
    for m in model:
        modelDict[str(m)] = model[m]
    for t in range(num_threads):
        print("For thread:", t)
        for i in range(len(trace)):
            if trace[i][-2]!=t:
                continue
            print("pc_"+str(trace[i][0]), modelDict["pc_"+str(trace[i][0])])
    return 0
    
def buildSolver(pcs, seq, pt, persist, locks, phi, assertions):
    solver = Solver()
    writerFile = open("../inputFiles/tempOutput.txt", "w")

    for i in itertools.chain(pcs, seq, pt, persist, locks, phi):
        solver.add(i)
        # print(i)
        # print(i)
    
    solver.add(Or(assertions))
    
    b1 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_4")<Int("pc_5"),
            Int("pc_3")<Int("pc_6"),

            Int("pc_4")<Int("pc_6"),
            Int("pc_7")<Int("pc_9"),

            Int("pc_4")<Int("pc_7"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b1)))

    b2 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_5")<Int("pc_4"), #modified
            Int("pc_3")<Int("pc_6"),

            Int("pc_4")<Int("pc_6"),
            Int("pc_7")<Int("pc_9"),

            Int("pc_4")<Int("pc_7"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b2)))

    b3 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_5")<Int("pc_4"), 
            Int("pc_3")<Int("pc_6"),

            Int("pc_6")<Int("pc_4"), #modified
            Int("pc_7")<Int("pc_9"),

            Int("pc_4")<Int("pc_7"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b3)))


    b4 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_5")<Int("pc_4"), 
            Int("pc_6")<Int("pc_3"),

            Int("pc_6")<Int("pc_4"), 
            Int("pc_7")<Int("pc_9"),

            Int("pc_7")<Int("pc_4"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b4)))


    b5 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_5")<Int("pc_4"), 
            Int("pc_3")<Int("pc_6"),

            Int("pc_6")<Int("pc_4"), 
            Int("pc_7")<Int("pc_9"),

            Int("pc_7")<Int("pc_4"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b5)))

    b6 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_5")<Int("pc_4"), 
            Int("pc_3")<Int("pc_6"),

            Int("pc_4")<Int("pc_6"), 
            Int("pc_7")<Int("pc_9"),

            Int("pc_7")<Int("pc_4"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b6)))

    b7 = [  Int("pc_1")<Int("pc_5"),
            Int("pc_5")<Int("pc_6"),
            # Int("pc_6")<Int("pc_7"),
            # Int("pc_7")<Int("pc_8"),

            Int("pc_2")<Int("pc_3"),
            Int("pc_3")<Int("pc_4"),
            # Int("pc_4")<Int("pc_9"),
            # Int("pc_9")<Int("pc_10"),

            Int("pc_4")<Int("pc_5"), 
            Int("pc_3")<Int("pc_6"),

            Int("pc_4")<Int("pc_6"), 
            Int("pc_7")<Int("pc_9"),

            Int("pc_7")<Int("pc_4"),
            Int("pc_6")<Int("pc_9")
    ]

    solver.add(Not(And(b7)))

    

    

                                      
    if solver.check()==sat:
        model = solver.model()
        modelAsserts = []
        for m in model:
            # print(m, type(m))
            modelAsserts.append(Int(str(m))!=model[m])

        solver.add(Or(modelAsserts))
        writerFile.write(str(modelAsserts)+"\n")
        print(str(modelAsserts)+"\n")
        formatModel(model, trace)
        # break
        # sorted_ref = printableSolver(solver)
        # print(sorted_ref)
    else:
        print("No such model exists.")
    return 0

if __name__ == "__main__":
    trace_file = "../inputFiles/trace-OPT.txt"
    assertion_file = "../inputFiles/PMConstraintViolations_trace-OPT.txt"

    trace = parseTrace(trace_file)
    trace = appendTrace(trace)

    assertions, phi = getAssertions(trace, assertion_file)
    pcs, seq, pt, persist, locks = buildConstraints(trace)

    print("Assertions: ", assertions, phi)

    # for t in trace:
    #     print(len(t), t)

    buildSolver(pcs, seq, pt, persist, locks, phi, assertions)

    



    # [11 != pt_1, 7 != pc_8, 4 != pc_5, 3 != pc_4, 8 != pc_3, 1 != pc_2, 5 != pc_6, 9 != pc_9, 2 != pc_1, 2 != pt_2, 6 != pc_7, 10 != pc_10]
