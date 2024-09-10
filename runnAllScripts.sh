make -f benchmarkMake -s -B
cd repair
make -f makeRepair -s -B
cat Report.txt
cd ../experiments
python3 convertResultsToCsv.py
cat ../experiments/results.csv