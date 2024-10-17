mv Report.txt Report_original.txt
touch Report.txt
echo "NUMBER OF THREADS: 2">Report.txt
python3 trace_formatter.py  ../experiments/fastFair/comparitive/fastFair_2.txt tempFastFair.txt
python3 step1.py tempFastFair.txt tempFastFair1.txt fastFair
python3 step4.py tempFastFair1.txt tempFastFair2.txt fastFair

# mv Report.txt Report_comparitive.txt