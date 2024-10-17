import sys

def clean(fileName):
    file = open(fileName, 'r')
    rows_toSend = []
    for row in file:
        if not ("Scope: entry" in str(row) or  "Scope: page" in str(row) or "Scope: header" in str(row) or "Scope: btree" in str(row)):
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
