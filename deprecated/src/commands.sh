python3 trace_formatter.py ../inputFiles/unformatted_trace.txt ../inputFiles/trace-OPT.txt
python3 PTimes.py ../inputFiles/trace-OPT.txt ../inputFiles/assertionsOPT.txt
python3 violationDetector.py ../inputFiles/trace-OPT.txt ../inputFiles/assertionsOPT.txt
