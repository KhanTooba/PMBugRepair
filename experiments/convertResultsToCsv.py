import os
import csv

def count_lines(filesList):
    line_counts = []
    for file in filesList:
        with open(file, 'r') as f:
            line_count = sum(1 for line in f)
            line_counts.append(line_count)
    return line_counts

def getLoc():
    directory = '../ThreadTrove/'
    files = [f for f in os.listdir(directory) ]

    listOfFiles = {}
    for file in files:
        listOfFiles[file] = count_lines([directory+file+"/"+file+".h", 
                                         "../results/outputs/"+file+"_output.txt"])
    listOfFiles['fastFair'] = count_lines(["../experiments/fastFair/btree.h",
                                           "../results/outputs/fastFair_output.txt"])
    listOfFiles['CCEH'] = count_lines(["../experiments/CCEH/src/CCEH.cpp",
                                           "../results/outputs/CCEH_output.txt"])
    
    all_Locs = count_lines(["../experiments/P-CLHT/src/clht_lb_res.c",
                            "../experiments/P-CLHT/src/clht_gc.c"])
    listOfFiles['P-CLHT'] = [sum(all_Locs), count_lines(["../results/outputs/P-CLHT_output.txt"])[0]]

    listOfFiles['Clevel_hashing'] = count_lines(["../experiments/ClevelHashing/test/src/clevel_hash_ycsb.cpp",
                                           "../results/outputs/Clevel_hashing_output.txt"])
    
    all_Locs = count_lines(["../experiments/memcached/src/memcached.c",
                            "../experiments/memcached/src/items.c"])
    listOfFiles['memcached'] = [sum(all_Locs), count_lines(["../results/outputs/memcached_output.txt"])[0]]
    
    return listOfFiles

def getFile():
    file = []
    for line in open("../repair/Report.txt"):
        file.append(str(line).replace("\n", ""))
    return file

def processSubset1(name, locDetails):
    # headers_1 = ["BenchmarkName", "LoC", "Trace Length", "#Loads", "#Stores", "#Threads", "#PM Vars"]
    data = []
    locDetail = locDetails[name]

    data = [name, locDetail[0], locDetail[1], 0, 0, 2, 0]
    return data

def processSubset2(name, subset):
    # headers_2 = ["BenchmarkName", "#DURA", "#MPB", "#MPA", "Repair time in Step 1", 
    #         "Repair time in Step 2", "#Calls in step 1", "#Calls in step 2", 
    #         "#Lock", "#sfence()", "#clflushopt()"]

    data = []
    dura = str(subset[0]).split(" ")[-1]
    mpb = str(subset[1]).split(" ")[-1]
    mpbFail = str(subset[3]).split(" ")[-1]
    duraFail = str(subset[2]).split(" ")[-1]
    t_dura = str(subset[4]).split(" ")[-2]
    t_mpb = str(subset[5]).split(" ")[-2]
    num_sfence = float(str(subset[6]).split(" ")[-1]) + float(str(subset[16]).split(" ")[-1])
    num_flush = str(subset[7]).split(" ")[-1]
    num_calls_1 = float(str(subset[8]).split(" ")[-1]) 
    
    mpa = str(subset[14]).split(" ")[-1]
    mpaFailed = str(subset[15]).split(" ")[-1]
    num_locks = str(subset[17]).split(" ")[-1]
    t_mpa = str(subset[19]).split(" ")[-2]
    num_calls_2 = float(str(subset[18]).split(" ")[-1])

    data = [name, int(dura), int(mpb), int(mpa), float(f"{float(t_dura)+float(t_mpb):.4f}"), 
            float(f"{float(t_mpa):.4f}"), int(num_calls_1), int(num_calls_2), int(num_locks), 
            int(num_sfence), int(num_flush)]
    return data

def processFile(file, locDetails):
    i = 0
    dataToSend1 = []
    dataToSend2 = []
    benchmarks = {}
    name = ""
    subset = []

    while i<len(file):
        if "Adding DURA & MPB Repair Report" in str(file[i]):
            subset = []
            name  = str(file[i]).split(" ")[-2].replace(":", "")
            for j in range(i+1, len(file)):
                if "Adding DURA & MPB Repair Report" in str(file[j]):
                    benchmarks[name] = subset
                    break
                i += 1
                subset.append(file[j])
        i += 1
    benchmarks[name] = subset

    for key in benchmarks.keys():
        print(key, len(benchmarks[key]))
        if len(benchmarks[key])>14:
            dataToSend1.append(processSubset1(key, locDetails))
            dataToSend2.append(processSubset2(key, benchmarks[key]))

    return dataToSend1, dataToSend2

if __name__ == "__main__":
    headers_1 = ["BenchmarkName", "LoC", "Trace Length", "#Loads", "#Stores", "#Threads", "#PM Vars"]
    
    headers_2 = ["BenchmarkName", "#DURA", "#MPB", "#MPA", "Repair time in Step 1", 
            "Repair time in Step 2", "#Calls in step 1", "#Calls in step 2", 
            "#Lock", "#sfence()", "#clflushopt()"]
    
    locDetails = getLoc()
    file = getFile()
    rows_1, rows_2 = processFile(file, locDetails)

    with open('results_table1.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers_1)  
        writer.writerows(rows_1)  

    with open('results_table2.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers_2)  
        writer.writerows(rows_2)  
    