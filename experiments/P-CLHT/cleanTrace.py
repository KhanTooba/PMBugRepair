import sys

def clean(fileName):
    file = open(fileName, 'r')
    rows_toSend = []
    count1, count2 = 0, 0
    for row in file:
        if "Scope: clht_hashtable_create" in str(row) and "@Ln,Col: 286" in str(row):
            count1 += 1
            if count1==1:
                rows_toSend.append(row)
        elif "Scope: clht_hashtable_create" in str(row) and "@Ln,Col: 282" in str(row):
            count2 += 1
            if count2==1:
                rows_toSend.append(row)
        else:
            rows_toSend.append(row)
    
    file.close()
    return rows_toSend

if __name__ == "__main__":
    inputFileName = sys.argv[1]
    outputFileName = sys.argv[2]
    rows = clean(inputFileName)

    file = open(outputFileName, 'w')
    file.writelines(rows)
    file.close()
