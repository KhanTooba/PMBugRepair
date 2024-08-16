import sys    

def format_STOREs(row, r):
    # Store: 0xb82306 Size: 2 ID: 2862 @Ln,Col: 564,22 Scope: insert_key; <Thread ID:140255810307904>
    stmt = []
    add = str(row).split(" ")[1]
    tid = str(row).split(":")[-1].split(">")[0]
    line = row.split("@")[1].split(":")[1].split(",")[0].strip()
    uid = str(row).split(" ")[5]
    stmt = [r, "STORE", add, tid, uid, line]
    return stmt

def format_FLUSH(row, r):
    stmt = []
    add = str(row).split(" ")[1]
    tid = str(row).split(":")[-1].split(">")[0]
    line = row.split("@")[1].split(":")[1].split(",")[0].strip()
    stmt = [r, "FLUSH", add, tid, line]
    return stmt

def format_FENCE(row, r):
    stmt = []
    tid = str(row).split(":")[-1].split(">")[0]
    line = row.split("@")[1].split(":")[1].split(",")[0].strip()
    stmt = [r, "FENCE", 0, tid, line]
    return stmt

def fileReader(name):
    f = open(name)
    contents = []
    loads = {}
    dependencies = {}
    r = 0
    for row in f:
        r += 1
        if "Load" in str(row) or "Store" in str(row):
            stmt = []
            # Load: 0xb82308 Size: 8 ID: 733 @Ln,Col: 573,11 Scope: store; <Thread ID:140255810307904>
            add = str(row).split(" ")[1]
            tid = str(row).split(":")[-1].split(">")[0]
            line = row.split("@")[1].split(":")[1].split(",")[0].strip()
            uid = str(row).split(" ")[5]
            stmt = [r, "LOAD", add, tid, line]
            loads[uid] = stmt
        
        if "Store" in str(row):
            stmt = format_STOREs(str(row), r)
            contents.append(stmt)
            
        elif "FLUSH" in str(row):
            stmt = format_FLUSH(str(row), r)
            contents.append(stmt)
        
        elif "FENCE" in str(row):
            stmt = format_FENCE(str(row), r)
            contents.append(stmt)
        
        elif "DEP" in str(row):
            # DEP: SrcID: 2554 DestID: 2495; <Thread ID:140255810307904>
            source = str(row).split(" ")[2]
            dest = str(row).split(" ")[4].split(";")[0]
            dependencies[dest] = source
    
    print("Total number of lines:", r)
    return contents, dependencies, loads

def getThreads(trace):
    threads = {}
    c = 0
    for t in trace:
        # print(t)
        if t[3] not in threads.keys():
            threads[t[3]] = c
            c += 1
    return threads

def format(trace, threads, dependencies, loads):
    # print(loads)
    traceFormatted = []
    dep = 0
    dep_set = []
    print(len(trace))
    for i in range(len(trace)):
        element = []
        if trace[i][1]=='LOAD':
            continue
        if trace[i][1] in ['FLUSH', 'FENCE']:
            element = [trace[i][0], trace[i][1], trace[i][2], -1, threads[trace[i][3]], trace[i][-1]]
        elif trace[i][1]=='STORE':
            element = [trace[i][0], trace[i][1], trace[i][2], -1, threads[trace[i][3]]]
            if trace[i][-2] in dependencies.keys():
                dest_id = dependencies[trace[i][-2]]
                element[2] = loads[dest_id][2]
                dep += 1
                if [trace[i], loads[dest_id]] not in dep_set:
                    dep_set.append([trace[i], loads[dest_id]])
            element.append(trace[i][-1])
            
        traceFormatted.append(element)

    print(len(traceFormatted))
    # for d in dep_set:
    #     print(d)
    print("Total unique dependencies: ", len(dep_set))
    print("Total dependencies: ", dep)

    
    ints = []
    index = []
    for t in traceFormatted:
        ints.append(int(t[-1]))
        index.append(int(t[0]))
        
    toreturn = []
    for t in traceFormatted:
        toreturn.append(t[1:])
    
    return toreturn

if __name__ == "__main__":
    inputFileName = sys.argv[1]
    outputFileName = sys.argv[2]
    trace, dependencies, loads = fileReader(inputFileName)
    threads = getThreads(trace)
    print(threads)
    trace = format(trace, threads, dependencies, loads)

    file = open(outputFileName, 'w')
    file.write("Threads: ["+str(threads)+"]\n")
    for t in trace:
        file.write(str(t)+"\n")
    file.close()