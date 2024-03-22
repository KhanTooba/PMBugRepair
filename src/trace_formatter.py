from sys import argv
import sys


def format_STOREs(row):
    stmt = []
    add = str(row).split(" ")[1]
    tid = str(row).split(":")[-1].split(">")[0]
    line = row.split("@")[1].split(":")[1].split(",")[0].strip()
    stmt = ["STORE", add, tid, line]
    return stmt

def format_LOADs(row):
    stmt = []
    add = str(row).split(" ")[1]
    tid = str(row).split(":")[-1].split(">")[0]
    line = row.split("@")[1].split(":")[1].split(",")[0].strip()
    stmt = ["LOAD", add, tid, line]
    return stmt

def format_FLUSH(row):
    stmt = []
    add = str(row).split(" ")[1]
    tid = str(row).split(":")[-1].split(">")[0]
    stmt = ["FLUSH", add, tid]
    return stmt

def format_FENCE(row):
    stmt = []
    tid = str(row).split(":")[-1].split(">")[0]
    stmt = ["FENCE", 0, tid]
    return stmt

def fileReader(name):
    f = open(name)
    contents = []
    for row in f:
        if "Load" in str(row):
            stmt = format_LOADs(str(row))
            contents.append(stmt)
        
        if "Store" in str(row):
            stmt = format_STOREs(str(row))
            contents.append(stmt)
            
        elif "FLUSH" in str(row):
            stmt = format_FLUSH(str(row))
            contents.append(stmt)
        
        elif "FENCE" in str(row):
            stmt = format_FENCE(str(row))
            contents.append(stmt)
    
    return contents

def getThreads(trace):
    threads = {}
    c = 0
    for t in trace:
        if t[2] not in threads.keys():
            threads[t[2]] = c
            c += 1
    return threads

def format(trace, threads):
    traceFormatted = []
    for t in trace:
        element = []
        if t[0]=='LOAD':
            continue
        if t[0] in ['FLUSH', 'FENCE']:
            element = [t[0], t[1], -1, threads[t[2]]]
        elif t[0]=='STORE':
            element = [t[0], t[1], -1, threads[t[2]]]
            for t2 in trace:
                if t2[0]=='LOAD' and t2[-1]==t[-1]:
                    # print('DEP found ',t2, t)
                    element[2] = t2[1]
        # print(element)
        traceFormatted.append(element)
    return traceFormatted

if __name__ == "__main__":
    inputFileName = sys.argv[1]
    outputFileName = sys.argv[2]
    trace = fileReader(inputFileName)
    threads = getThreads(trace)
    print(threads)
    trace = format(trace, threads)

    file = open(outputFileName, 'w')
    for t in trace:
        file.write(str(t)+"\n")
    file.close()

    print("Formatted trace:")
    for t in trace:
        print(t)