python3 cleanTrace.py /Users/toobakhan/Downloads/PMBugRepair/results/outputs/P-CLHT_output.txt tempP-CLHT0.txt
python3 trace_formatter.py tempP-CLHT0.txt tempP-CLHT.txt
python3 step1.py tempP-CLHT.txt tempP-CLHT1.txt P-CLHT
python3 step4.py tempP-CLHT1.txt tempP-CLHT2.txt P-CLHT