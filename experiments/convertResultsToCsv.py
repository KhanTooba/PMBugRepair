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
    return listOfFiles

def getFile():
    file = []
    for line in open("../repair/Report.txt"):
        file.append(str(line).replace("\n", ""))
    return file

def processSubset(name, subset, locDetails):
    data = []
    dura = str(subset[0]).split(" ")[-1]
    mpb = str(subset[1]).split(" ")[-1]
    t_dura = str(subset[2]).split(" ")[-2]
    t_mpb = str(subset[3]).split(" ")[-2]
    num_sfence = float(str(subset[4]).split(" ")[-1]) + float(str(subset[13]).split(" ")[-1])
    num_flush = str(subset[5]).split(" ")[-1]
    num_calls_1 = float(str(subset[6]).split(" ")[-1]) 
    mpa = str(subset[12]).split(" ")[-1]
    num_locks = str(subset[14]).split(" ")[-1]
    t_mpa = str(subset[16]).split(" ")[-2]
    num_calls_2 = float(str(subset[15]).split(" ")[-1])
    locDetail = locDetails[name]

    data = [name, int(dura), int(mpb), int(mpa), float(f"{float(t_dura)+float(t_mpb):.4f}"), 
            float(f"{float(t_mpa):.4f}"), int(num_calls_1), int(num_calls_2), int(num_locks), 
            int(num_sfence), int(num_flush), locDetail[0], locDetail[1]]
    return data

def processFile(file, locDetails):
    i = 0
    dataToSend = []
    benchmarks = {}

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

    for key in benchmarks.keys():
        dataToSend.append(processSubset(key, benchmarks[key], locDetails))

    return dataToSend

if __name__ == "__main__":
    headers = ["BenchmarkName", "#DURA", "#MPB", "#MPA", "Repair time in Step 1", 
            "Repair time in Step 2", "#Calls in step 1", "#Calls in step 2", 
            "#Lock", "#sfence()", "#clflushopt()", "LoC", "Trace Length"]
    
    locDetails = getLoc()
    file = getFile()
    rows = processFile(file, locDetails)

    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)  
        writer.writerows(rows)  
    