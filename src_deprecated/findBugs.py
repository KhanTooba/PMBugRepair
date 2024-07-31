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

def addSequentialConstraints(firstTrace, secondTrace, firstStmt, lastStmt, trace):
    constraintStmt, sequential = [], []

    for i in range(0, len(firstTrace)):
        var = Int("var_"+str(firstTrace[i]))
        constraintStmt.append(var)
        if i>0:
            sequential.append(var>constraintStmt[-2])

    for i in range(0, len(secondTrace)):
        var = Int("var_"+str(secondTrace[i]))
        constraintStmt.append(var)
        if i>0:
            sequential.append(var>constraintStmt[-2])

    for var in constraintStmt:
        sequential.append(var>=firstStmt)
        sequential.append(var<=lastStmt)
        for var2 in constraintStmt:
            if str(var2)!=str(var):
                sequential.append(var2!=var)

    for i in range(lastStmt):
        if trace[i][1]==103:
            for j in range(lastStmt):
                if trace[j][-1]==trace[i][-1] and trace[j][0]>trace[i][0]:
                    sequential.append(Int("var_"+str(i+1))<Int("var_"+str(j+1)))
                    # Theses are constraints to maintain property of fences

    return sequential, constraintStmt

def addConcurrencyConstraints(trace):
    concurrent = []
    for i in range(0, len(trace)):
        if trace[i][1]==100:
            for j in range(i-1, 0, -1):
                if trace[j][1]==101 and trace[i][3]==trace[j][2]:
                    concurrent.append(Int("var_"+str(i+1))>Int("var_"+str(j+1)))
                    # print("Adding ", Int("var_"+str(i+1))>Int("var_"+str(j+1)))
                    break
    
    return concurrent

def addPersistencyConstraints(trace, lastStmt):
    persist = []

    for i in range(lastStmt):
        if trace[i][1]==101:
            for j in range(i+1, lastStmt):
                if trace[j][1]==101 and trace[j][2]==trace[i][2]:
                    break
                if trace[j][1]==100 and trace[j][3]==trace[i][2]: 
                    #If the load is reading from a variable, then we go on and find an appropriate flush
                    for k in range(i, lastStmt):
                        if trace[k][1]==102 and trace[k][2]==trace[i][2]: 
                            #If a clflush is found, we add constraint that the clflush should always take place before the load
                            persist.append(Int("var_"+str(j+1))>Int("var_"+str(k+1)))
    return persist

def addConstraints(inputFileName, outputFileName):
    trace = parseTrace(inputFileName)
    writer = open(outputFileName, 'w+')
    # print(trace)
    solver = Solver()
    firstStmt = trace[0][0]
    lastStmt = trace[-1][0]

    """
    Stores PM, concurrency and sequenctial constrains respectively. At any point in the program, 
    print these lists to find out which constraints have been added and what is their purpose.
    """

    c = 1
    firstTrace = []
    secondTrace = []

    for t in trace:
        if t[-1]==1:
            firstTrace.append(t[0])
        else:
            secondTrace.append(t[0])

    sequential, constraintStmt = addSequentialConstraints(firstTrace, secondTrace, firstStmt, lastStmt, trace)

    solver.add(sequential)
    """
    At this point, sequential constraints, 
    i.e constraints of program statements of a single thread have been added.
    Now, adding concurrency constraints. 
    """
    concurrent = addConcurrencyConstraints(trace)
    solver.add(concurrent)

    """
    Concurrency constraints added. 
    Now adding PM constraints. PM constraints have to be negated and then added to the solver to get counter examples.
    """
    persist = addPersistencyConstraints(trace, lastStmt)

    s2 = Solver()
    s2.add(sequential)
    s2.add(concurrent)
    
    print("PM Constraints are: ", persist)
    s2.add(persist)

    print("\nThe following executions satisfy PM Properties:")
    numSols = printAllSolutions(s2, lastStmt, writer)
    print(numSols, " solutions violate PM properties.\n")
    # writer.close()


    print("PM Constraints are: ", persist)
    solver.add((Not(And(persist))))

    print("\nThe following executions violate PM Properties:")
    numSols = printAllSolutions(solver, lastStmt, writer)
    print(numSols, " solutions violate PM properties.\n")
    writer.close()

if __name__ == "__main__":
    inputFileName = "../inputFiles/"+sys.argv[1]         # "trace-1.txt"
    outputFileName = "../outputFiles/"+sys.argv[1]   
    addConstraints(inputFileName, outputFileName)

"""
Conceptual question: 
Is it ohk for statement 6 to execute after 4 and before 5. Or is it important to maintain the fencing.
"""