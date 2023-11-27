from z3 import *
import sys, os


"""
Values for standard statements:
LOAD    100
STORE   101
CLFLUSH 102
SFENCE  103
"""

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
    if elements[0]=="LOAD":
        traceParsed.append(100)
    elif elements[0]=="STORE":
        traceParsed.append(101)
    elif elements[0]=="CLFLUSH":
        traceParsed.append(102)
    elif elements[0]=="SFENCE":
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

def findPCRanges(outputFileName, trace):
    pc = 1
    current_thread = 1
    lower, upper = 1, 1
    non_flush_PC = 1
    PCs = []

    for stmt in range(1, len(trace)+1):
        if(trace[stmt-1][-1]!=current_thread):
            #print("Swapping threads")
            current_thread = trace[stmt-1][-1]
        #print(stmt, pc, trace[stmt-1][-1])
        if(trace[stmt-1][1]==100 or trace[stmt-1][1]==101):
            #print(stmt,":\t>=", non_flush_PC, ",\t<=", upper, "\t", non_flush_PC)
            PCs.append(Int("Stmt_"+str(stmt))>=non_flush_PC)
            PCs.append(Int("Stmt_"+str(stmt))<=upper)
            non_flush_PC += 1
        else:
            #print(stmt,":\t>=",lower)
            PCs.append(Int("Stmt_"+str(stmt))>=lower)
        
        lower += 1
        upper += 1
        
        #Adding fence semantics
        if(trace[stmt-1][1]==103):
            non_flush_PC = stmt+1
            for j in range(1, stmt):
                #print(j, "\t< PC_", stmt, "\t", non_flush_PC)
                PCs.append(Int("Stmt_"+str(j))<=Int("Stmt_"+str(stmt)))
                
        
    for c in PCs:
        print(c)
    
    return PCs

def findLowerUpperBounds(outputFileName, trace):
    PC_lower, PC_upper = [], []
    constraints = []
    for stmt in range(0, len(trace)):
        lower = -1
        upper = 999
        if(trace[stmt][1]==101):
            for j in range(stmt+1, len(trace)):
                if(trace[j][1]==102 and trace[stmt][2]==trace[j][2]):
                    lower = j+1
                
                if(trace[j][1]==103):
                    upper = j+1
                    break
        
        if(trace[stmt][1]==100):
            lower = stmt+1

        if(lower!=-1):
            PC_lower.append(Int("lower_"+str(stmt+1))>=Int("Stmt_"+str(lower)))
        else:
            PC_lower.append(Int("lower_"+str(stmt+1))<=-1)
        if(upper!=999):
            PC_upper.append(Int("Upper_"+str(stmt+1))>=Int("Stmt_"+str(lower)))
        else:
            PC_upper.append(Int("Upper_"+str(stmt+1))>=999)
        
        PC_lower.append(Int("lower_"+str(stmt+1))>=-1)
        PC_upper.append(Int("Upper_"+str(stmt+1))<=999)
    
    for i in range(len(PC_lower)):
        print(PC_lower[i], PC_upper[i])
    
    return PC_lower, PC_upper

def durability(outputFileName, trace):
    durable = []
    for stmt in range(0, len(trace)):
        if(trace[stmt][1]==101):
            durable.append(Int("lower_"+str(stmt+1))==-1)
    
    print("Durability constraints:")
    for d in durable:
        print(d)
    
    return durable

def crashConsistency(outputFileName, trace):
    crash = []
    for stmt in range(0, len(trace)):
        if(trace[stmt][1]==101):
            for j in range(stmt+1, len(trace)):
                if(trace[j][1]==101 and trace[stmt][2]==trace[j][2]):
                    break
                if(trace[j][1]==100 and trace[stmt][2]==trace[j][3]):
                    crash.append(Not(Int("Upper_"+str(stmt+1))<Int("lower_"+str(j+1))))
    print("Printing crash consistency constraints:")
    for c in crash:
        print(c)
    return crash

def constructAllConstraints(inputFileName, outputFileName):
    writer = open(outputFileName, 'w+')
    trace = parseTrace(inputFileName)
    PCs = findPCRanges(outputFileName, trace)
    PC_lower, PC_upper = findLowerUpperBounds(outputFileName, trace)
    durable = durability(outputFileName, trace)
    crash = crashConsistency(outputFileName, trace)
    violatedConstraints = []

    solver = Solver()
    solver.add(PCs)
    solver.add(PC_lower)
    solver.add(PC_upper)
    for c in crash:
        durable.append(c)
    solver.add(Or(durable))
    # solver.add(crash)
    print(solver)
    print("\nThe following execution violates PM Properties:")
    # print(solver)
    if solver.check()==sat:
        model = solver.model()
        print(model)
        print("\nPrinting PM constraints which could be violated:")
        for a in solver.assertions():
            if is_or(a):
                for child in a.children():
                    print(child)
                    if is_true(model.eval(child)):
                        # print("True",child)
                        violatedConstraints.append(child)


    else:
        print("UNSAT")
    
    print("\nPrinting constraints which were violated:")
    print(violatedConstraints)
    # numSols = printAllSolutions(solver, 7, writer)
    # print(numSols, " solutions violate PM properties.\n")

def constructAllConstraintsUNSATCoreWay(inputFileName, outputFileName):
    writer = open(outputFileName, 'w+')
    trace = parseTrace(inputFileName)
    PCs = findPCRanges(outputFileName, trace)
    PC_lower, PC_upper = findLowerUpperBounds(outputFileName, trace)
    durable = durability(outputFileName, trace)
    crash = crashConsistency(outputFileName, trace)

    s = Solver()
    s.set(unsat_core=True)
    counter = 1
    for constr in PCs:
        s.assert_and_track(constr, 'a'+str(counter))
        counter += 1
    
    for constr in PC_upper:
        s.assert_and_track(constr, 'a'+str(counter))
        counter += 1
    
    for constr in PC_lower:
        s.assert_and_track(constr, 'a'+str(counter))
        counter += 1

    # for constr in durable:
    #     s.assert_and_track(constr, 'a'+str(counter))
    #     counter += 1
    
    for constr in crash:
        s.assert_and_track(constr, 'a'+str(counter))
        counter += 1
    
    result = s.check()
    print(s)
    print(result)
    print(type(s))
    if result == unsat : 
        c = s.unsat_core()
        print(c)
        # for x in c:
        #     print(s.model()[x])
    
if __name__ == "__main__":
    inputFileName = "../inputFiles/"+sys.argv[1]         #"trace-1.txt"
    outputFileName = "../outputFiles/"+sys.argv[1]   
    # addConstraints(inputFileName, outputFileName)
    constructAllConstraints(inputFileName, outputFileName)
    # constructAllConstraintsUNSATCoreWay(inputFileName, outputFileName)

