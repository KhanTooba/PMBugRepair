from sys import argv
import sys

class Graph:
    def __init__(self):
        self.graph = {}

    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, u, v):
        if u in self.graph:
            if v not in self.graph[u]:
                self.graph[u].append(v)
        else:
            self.graph[u] = [v]

    def __str__(self):
        return str(self.graph)

    def has_cycle_directed(self):
        visited = set()
        rec_stack = set()
        
        def dfs(v):
            if v in rec_stack:
                return True
            if v in visited:
                return False
            
            visited.add(v)
            rec_stack.add(v)
            for neighbor in self.graph.get(v, []):
                if dfs(neighbor):
                    return True
            rec_stack.remove(v)
            return False
        
        for node in self.graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def has_cycle_undirected(self):
        visited = set()

        def dfs(v, parent):
            visited.add(v)
            for neighbor in self.graph.get(v, []):
                if neighbor not in visited:
                    if dfs(neighbor, v):
                        return True
                elif neighbor != parent:
                    return True
            return False

        for node in self.graph:
            if node not in visited:
                if dfs(node, None):
                    return True
        return False

    def dfs_traversal(self, start_node):
        visited = set()
        traversal_order = []

        def dfs(node):
            if node not in visited:
                visited.add(node)
                traversal_order.append(node)
                for neighbor in self.graph.get(node, []):
                    dfs(neighbor)

        dfs(start_node)
        return traversal_order

    def find_cycles(self):
        def dfs(node, current_path, visited, cycles):
            visited[node] = True
            current_path.append(node)
            
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, current_path, visited, cycles)
                elif neighbor in current_path:
                    # Found a cycle
                    cycle_start_index = current_path.index(neighbor)
                    cycle = current_path[cycle_start_index:]
                    cycles.append(cycle)
                    
            current_path.pop()
            visited[node] = False

        visited = {}
        cycles = []
        for node in self.graph:
            if node not in visited:
                dfs(node, [], visited, cycles)
        return cycles
    

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

def condense_cycles(int_list, index_list):
    seen = {}
    result_nums = []
    result_index = []
    
    i = 0
    while i < len(int_list):
        num = int_list[i]
        index = index_list[i]
        if num in seen:
            cycle_start = seen[num]
            cycle = int_list[cycle_start:i]
            
            # Find the first non-repeating sequence after the cycle ends
            j = i
            while j < len(int_list) and int_list[j] in seen:
                j += 1

            # Add the cycle and the first non-repeating element to the result
            result_nums += cycle
            result_index += index_list[cycle_start:i]
            # print(cycle)
            if j < len(int_list):
                result_nums.append(int_list[j])
                result_index.append(index_list[j])
                seen[int_list[j]] = len(result_nums) - 1
            i = j
        else:
            seen[num] = len(result_nums)
            result_nums.append(num)
            result_index.append(index)
            i += 1

    print(len(result_nums), len(result_index))
    return result_nums, result_index

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

    g = Graph()
    # for t in traceFormatted:
    #     print(t)
    #     g.add_node(int(t[-1]))
    # for i in range(0, len(traceFormatted)-1):
    #     g.add_edge(int(traceFormatted[i][-1]), int(traceFormatted[i+1][-1]))

    ints = []
    index = []
    for t in traceFormatted:
        ints.append(int(t[-1]))
        index.append(int(t[0]))
    
    # print(len(ints))
    # ints, index = condense_cycles(ints, index)
    # # print(index)
    # finalTrace = []
    # traceDict = {}
    # for t in traceFormatted:
    #     traceDict[int(t[0])] = t
    
    # for i in index:
    #     finalTrace.append(traceDict[i][1:])
    #     print(traceDict[i][1:])
        
    toreturn = []
    for t in traceFormatted:
        toreturn.append(t[1:])
    # print(g)
    # print("Has cycle (directed):", g.has_cycle_directed())
    # print(g.find_cycles())
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