# PMBugRepair

To generate trace for all benchmarks in the benchmark folder: 
```
#########################################################################
# Generate traces: 
#########################################################################
make -f benchmarkMake -s -B
# Results will be saved in PMC/benchmark/bcFiles/outputs
```

To execute step1 (repair individual traces) for all benchmarks in the benchmark folder: 
```
#########################################################################
# Generate traces: 
#########################################################################
cd repair
make -f makeRepair -s -B
# Results will be saved in PMC/benchmark/bcFiles/results
```

