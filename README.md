# PMBugRepair

## Ongoing work: Baseline version.

To build the trace generator llvm opt pass: 
```
# Build opt pass: 
#########################################################################
sh builder.sh
# Results will be saved in PMBugRepair/build
```

To generate trace for all benchmarks in the benchmark folder: 
```
# Generate traces: 
#########################################################################
make -f benchmarkMake -s -B
# Results will be saved in PMBugRepair/benchmark/bcFiles/outputs
```

To execute step1 (repair individual traces) for all benchmarks in the benchmark folder: 
```
# Execute step 1: 
#########################################################################
cd repair
make -f makeRepair -s -B
# Results will be saved in PMBugRepair/benchmark/bcFiles/results
```

Updates:
1. DURA, MPB and MPB bug repair has been added.
2. Results verified on programs under benchmark folder and FAST FAIR benchmark.
3. Results pending for the remaining ASPLOS benchmarks.