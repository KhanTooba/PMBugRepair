from z3 import *

"""
Reads DURA, MPB & MPA bugs from their respective bug files and constructs bug constraints from them.
"""

def readBugs(name, trace, inf):
    index = {}
    totalMPB, totalDURA, failedMPB, failedDURA = 0, 0, 0, 0

    for t in trace:
        if str(t[-1])[0] == "_" and t[-1][1:] not in index.keys():
            index[t[-1][1:]] = t[0]
        elif t[-1] not in index.keys():
            index[t[-1]] = t[0]


    bugs = []
    lines = []
    for line in open(name):
        lines.append(line.replace("\n", "").strip())
    i = 0
    while i<(len(lines)):
        line = lines[i]
        if str(lines[i])[-1]=="<":
            line = line+lines[i+1]
            i += 2
        else:
            i += 1
        if "< 9999" in line:
            try:
                if "pt__" in str(line):
                    data = index[str(line).split("<")[0].replace("pt__", "").strip()]
                else:
                    data = index[str(line).split("<")[0].replace("pt_", "").strip()]
                bugs.append(Int("pt_"+str(data))<inf)
                totalDURA += 1
            except:
                totalDURA += 1
                failedDURA += 1
         
        else:
            try:  
                if "pt__" in str(str(line).split("<")[0]):
                    first = index[str(line).split("<")[0].replace("pt__", "").strip()]
                else:
                    first = index[str(line).split("<")[0].replace("pt_", "").strip()]

                if "pt__" in str(str(line).split("<")[1]):
                    second = index[str(line).split("<")[1].replace("pt__", "").strip()]
                else:
                    second = index[str(line).split("<")[1].replace("pt_", "").strip()]
                
                bugs.append(Int("pt_"+str(first))<Int("pt_"+str(second)))
                totalMPB += 1
            except:
                totalMPB += 1
                failedMPB += 1
    return bugs, totalMPB, totalDURA, failedMPB, failedDURA 

def readMPAs(name, trace):
    bugs = []
    bugInfos = {}
    index = {}
    totalMPA, failedMPA = 0, 0

    firstOcc = {}
    for t in trace:
        if t[-1] not in firstOcc.keys():
            firstOcc[t[-1]] = t

    for t in trace:
        if str(t[-1])[0] == "_" and t[-1][1:] not in index.keys():
            index[t[-1][1:]] = t[0]
        elif t[-1] not in index.keys():
            index[t[-1]] = t[0]

    bugs = []
    writes, reads = [], []
    lines = []
    for line in open(name):
        lines.append(line.replace("\n", "").strip())
    
    i = 0
    while i<(len(lines)):

        line = lines[i]
        if str(lines[i])[-1]!=")":
            line = line+lines[i+1]
            i += 2
        else:
            i += 1
        
        data = line.split(",")[0].replace("And(", "").split("<")
        first = data[0].replace("pc_", "").strip()
        second = data[1].replace("pc_", "").strip()
        if first in index.keys() and second in index.keys():
            bugs.append(And(Int("pc_"+str(index[first]))<Int("pc_"+str(index[second])), 
                            Int("pt_"+str(index[first]))>Int("pc_"+str(index[second]))))
            bugInfos[str(index[first])+"-"+str(index[second])] = [firstOcc[first], firstOcc[second]]
            if firstOcc[first][0] not in writes:
                writes.append(firstOcc[first][0])
            if firstOcc[second][0] not in reads:
                reads.append(firstOcc[second][0])
                        
            totalMPA += 1
        else:
            totalMPA += 1
            failedMPA += 1

    return bugs, totalMPA, failedMPA, bugInfos, writes, reads