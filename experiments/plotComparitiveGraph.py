import matplotlib.pyplot as plt
import numpy as np

def count_lines(path, filesList):
    line_counts = []
    for file in filesList:
        with open(path+file, 'r') as f:
            line_count = sum(1 for line in f)
            line_counts.append(line_count)
    return line_counts

def readTimes():
    numThreads = [i for i in range(2, 65, 2)]
    step1 = []
    step4 = []
    for line in open("ComparitiveResults.txt"):
        step1.append(float(str(line).split(",")[1].strip()))
        step4.append(float(str(line).replace("\n", "").split(",")[2].strip()))
    return numThreads, step1, step4

def plotLinearGraph(x, y1, y2):
    plt.plot(x, y1, label='Time taken to repair DURA and MPB bugs', color='blue') 
    plt.plot(x, y2, label='Time taken to repair MPA bugs', color='green') 

    plt.xlabel('Number of threads')
    plt.ylabel('Time taken to repair bugs')
    plt.title('Time taken to repair bugs v/s number of threads')

    plt.legend()
    plt.savefig('linear_graph.png')
    plt.clf()

def plotBarGraph(x, y1, y2):
    x = np.array(x)
    y1 = np.array(y1)
    y2 = np.array(y2)
    bar_width = 0.35
    plt.bar(x - bar_width/2, y1, width=bar_width, label='Time taken to repair DURA and MPB bugs', color='blue')
    plt.bar(x + bar_width/2, y2, width=bar_width, label='Time taken to repair MPA bugs', color='green')  

    plt.xlabel('Number of threads')
    plt.ylabel('Time taken to repair bugs')
    plt.title('Time taken to repair bugs v/s number of threads')    

    plt.xticks(x, x)  
    plt.legend()
    plt.savefig('bar_graph.png')
    plt.clf()


if __name__ == "__main__":
    path = "fastFair/comparitive/"
    fileNames = ["fastFair_"+str(i)+".txt" for i in range(2, 65, 2)]
    locs = count_lines(path, fileNames)
    numThreads, step1, step4 = readTimes()
    plotLinearGraph(numThreads, step1, step4)
    plotBarGraph(numThreads, step1, step4)