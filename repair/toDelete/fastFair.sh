python3 cleanTrace.py /Users/toobakhan/Downloads/PMBugRepair/results/outputs/fastFair_output.txt tempFastFair0.txt
python3 trace_formatter.py tempFastFair0.txt tempFastFair.txt
python3 step1.py tempFastFair.txt tempFastFair1.txt fastFair
python3 step4.py tempFastFair1.txt tempFastFair2.txt fastFair