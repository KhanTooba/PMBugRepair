from z3 import *
import sys, os


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
violations = []
duras = []
mpbs = []

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
        # writer.write(str(model))
        # writer.write("\n")
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
    8. trace[i][5] = Line number
    """
    trace_file = open(file)
    trace = []
    counter = 1
    # print("Printing here")
    for line in trace_file:
        if "threads" in line:
            global num_threads
            num_threads = int(line.split(":")[1].strip())
            continue
        # print(line)
        elements = line.strip("[]\n").split(",")
        # print(elements)
        # print(parseTraceHelper(elements, counter))
        trace.append(parseTraceHelper(elements, counter))
        counter += 1

    return trace

def findPCRanges(writer, trace):
    pc = 1
    current_thread = 1
    lower, upper = 1, 1
    non_flush_PC = 1
    PCs = []

    for stmt in range(1, len(trace)+1):
        # print(stmt)
        if(trace[stmt-1][-2]!=current_thread):
            #print("Swapping threads")
            current_thread = trace[stmt-1][-2]
        #print(stmt, pc, trace[stmt-1][-2])
        if(trace[stmt-1][1]==100 or trace[stmt-1][1]==101 or trace[stmt-1][1]==104 or trace[stmt-1][1]==105):
            #print(stmt,":\t>=", non_flush_PC, ",\t<=", upper, "\t", non_flush_PC)
            PCs.append(Int("Stmt_"+str(stmt))>=non_flush_PC)
            PCs.append(Int("Stmt_"+str(stmt))<=upper)
            non_flush_PC += 1
        else:
            #print(stmt,":\t>=",lower)
            PCs.append(Int("Stmt_"+str(stmt))>=lower)
            PCs.append(Int("Stmt_"+str(stmt))<=upper)
        
        lower += 1
        upper += 1
        
        #Adding fence semantics
        if(trace[stmt-1][1]==103):
            # print("Adding fence semantics")
            non_flush_PC = stmt+1
            for j in range(1, stmt+1):
                #print(j, "\t< PC_", stmt, "\t", non_flush_PC)
                PCs.append(Int("Stmt_"+str(j))<=Int("Stmt_"+str(stmt)))
                
    # writer.write("Printing the range of Program counters each statement can take:\n")
    # for c in PCs:
    #     writer.write(str(c)+"\n")
    
    return PCs

def findLowerUpperBounds(writer, trace):
    PC_lower, PC_upper = [], []
    constraints = []
    for stmt in range(0, len(trace)):
        # print(trace[stmt])
        upper = 999
        flag = -1
        if(trace[stmt][1]==101):
            # print("For statement STORE at ", stmt)
            for j in range(stmt+1, len(trace)):
                
                if(trace[j][1]==102 and trace[stmt][2]==trace[j][2]):
                    flag = 1
                
                if(trace[j][1]==103 and flag==1):
                    upper = j+1
                    # print(upper)
                    break

        PC_lower.append(Int("lower_"+str(stmt+1))==Int("Stmt_"+str(stmt+1)))

        if(upper!=999):
            PC_upper.append(Int("Upper_"+str(stmt+1))==Int("Stmt_"+str(upper)))
        else:
            PC_upper.append(Int("Upper_"+str(stmt+1))>=999)

        # PC_upper.append(Int("Upper_"+str(stmt+1))<999)
    
    # writer.write("\nPrinting constraints on Persistent Times upper and lower bounds:\n")
    # for i in range(len(PC_lower)):
    #     writer.write(str(PC_lower[i])+"\t"+str(PC_upper[i])+"\n")
    
    return PC_lower, PC_upper


def durability(writer, trace):
    durable = []
    for stmt in range(0, len(trace)):
        if(trace[stmt][1]==101):
            durable.append(Int("Upper_"+str(stmt+1))>=999)
    
    return durable

def crashConsistency(writer, trace):
    crash = []
    for stmt in range(0, len(trace)):
        flag = 0
        t_id = trace[stmt][-2]
        if(trace[stmt][1]==101):
            for j in range(stmt+1, len(trace)):
                if(trace[j][1]==103):
                    flag = 1
                if(t_id == trace[j][-2] and flag==1):
                    continue
                if(trace[j][1]==101 and trace[stmt][2]==trace[j][3]):
                    crash.append(Not(Int("Upper_"+str(stmt+1))<Int("lower_"+str(j+1))))
                if(trace[j][1]==100 and trace[stmt][2]==trace[j][3]):
                    crash.append(Not(Int("Upper_"+str(stmt+1))<Int("lower_"+str(j+1))))

    return crash

def makeAnotherSolver(solver, constr):
    s = Solver()
    for c in solver.assertions():
        if is_or(c):
            or_constr = []
            for child in c.children():
                if str(child)!=str(constr):
                    or_constr.append(child)
            s.add(Or(or_constr))
        else:
            s.add(c)
                
    return s

def comprehendViolation(constr, writer, trace):

    if "<" in str(constr):
        stmts_by_trace = []

        for i in range(num_threads):
            stmts_by_trace.append([])

        for t in trace:
            t_id = t[-2]
            stmt = t[0]
            stmts_by_trace[t_id].append(stmt)

        stmts_1 = int(str(constr).split("_")[1].split("<")[0])
        stmts_2 = int(str(constr).split("_")[2].split(")")[0])
        t_1, t_2 = 0, 0
        for i in range(num_threads):
            if stmts_1 in stmts_by_trace[i]:
                t_1 = i
            if stmts_2 in stmts_by_trace[i]:
                t_2 = i
        
        # if t_1==t_2:
        #     writer.write("[MPB:"+str(trace[stmts_1-1][2])+"<"+str(trace[stmts_2-1][2])+"]\n")
        
        # else:
        #     writer.write("[MPB:"+str(trace[stmts_1-1][2])+"<"+str(trace[stmts_2-1][2])+"]\n")
        
        # if str(trace[stmts_1-1][2]) not in violations.keys():
        #     violations[str(trace[stmts_1-1][2])] = []
        # else:
        #     violations[str(trace[stmts_1-1][2])].append()
        element = [str(trace[stmts_1-1][2]), str(trace[stmts_2-1][2]), str(trace[stmts_1-1][-1]), str(trace[stmts_2-1][-1])]
        if [str(trace[stmts_1-1][-1]), str(trace[stmts_2-1][-1])] not in mpbs:
            mpbs.append([str(trace[stmts_1-1][-1]), str(trace[stmts_2-1][-1])])
            violations.append(element)
            print(element)

    else:
        stmt = int(str(constr).split("_")[1].split(" ")[0])
        trace_element = trace[stmt-1]
        # writer.write("[DURA:"+str(trace_element[2])+"]\n")
        element = [str(trace_element[2]), "DURA", trace_element[-1]]
        # if element not in violations:
        #     violations.append(element)
        if ["DURA", trace_element[-1]] not in duras:
            # print("Here, ", duras)
            print(element)
            duras.append(["DURA", trace_element[-1]])
            violations.append(element)
        # if str(trace_element[2]) not in violations.keys():
        #     violations[str(trace_element[2])] = ["DURA"]
        # else:
        #     violations[str(trace_element[2])].append("DURA")
    
    

def lockSemantics(writer, trace):
    locks = []
    for stmt in range(0, len(trace)):
        flag = 0
        t_id = trace[stmt][-2]
        if(trace[stmt][1]==104):
            counter = 1
            for j in range(stmt+1, len(trace)):
                locks.append(Int("Stmt_"+str(j))==Int("Stmt_"+str(stmt))+counter)
                counter += 1
                if(trace[j][1]==105):
                    break
    return locks

def constructAllConstraints(inputFileName, outputFileName):
    writer = open(outputFileName, 'w+')
    trace = parseTrace(inputFileName)
    PCs = findPCRanges(writer, trace)
    PC_lower, PC_upper = findLowerUpperBounds(writer, trace)
    durable = durability(writer, trace)
    crash = crashConsistency(writer, trace)
    lock = lockSemantics(writer, trace)
    print("All constraints generated")
    violatedConstraints = []

    solver = Solver()
    solver.add(PCs)
    solver.add(PC_lower)
    solver.add(PC_upper)
    solver.add(lock)

    durable = []
    for c in crash:
        durable.append(c)
    solver.add(Or(durable))

    print("Thread count:", num_threads)

    exec = 0
    while solver.check()==sat:
        model = solver.model()
        for a in solver.assertions():
            if is_or(a):
                for child in a.children():
                    if is_true(model.eval(child)):
                        print("Run count: ", exec)
                        # print(duras, violations)
                        comprehendViolation(child, writer, trace)
                        # print(duras, violations)
                        exec += 1
                        solver = makeAnotherSolver(solver, child)
    
    for v in violations:
        # print(v)
        if 'DURA' in str(v):
            writer.write("[DURA:"+v[0]+","+str(v[2])+"]\n")
        else:
            writer.write("[MPB:"+v[0]+"<"+v[1]+"]\n")

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
    # inputFileName = "../inputFiles/"+sys.argv[1]         #"trace-1.txt"
    # outputFileName = "../inputFiles/"+sys.argv[2]   
    inputFileName = sys.argv[1]         #"trace-1.txt"
    outputFileName = sys.argv[2] 
    # addConstraints(inputFileName, outputFileName)
    constructAllConstraints(inputFileName, outputFileName)
    # constructAllConstraintsUNSATCoreWay(inputFileName, outputFileName)
