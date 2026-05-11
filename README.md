# Symbolic Analysis for Repairing Persistent Memory Bugs in Concurrent Programs
## [To Appear in: SANER 2026]

To build the trace generator llvm opt pass: 
```
# Build opt pass (Results will be saved in PMBugRepair/build): 
    sh builder.sh
```

To generate traces for all benchmarks in the ThreadTrove folder: 
```
# Generate traces (Results will be saved in PMBugRepair/results/bcFiles/outputs): 
    make -f benchmarkMake -s -B
```

To generate traces for all RealWorld benchmarks (FastFair, and CCEH): 
```
# Generate traces (Results will be saved in PMBugRepair/results/bcFiles/outputs): 
    sudo sh makeRealWorld.sh
```

To execute step1 (repair individual traces) and step 4 (repair MPA bugs) for all benchmarks in the ThreadTrove folder and realWorld benchmarks: 
```
# Step 1 Results will be saved in PMBugRepair/results/bcFiles/results 
# Step 4 Results will be saved in PMBugRepair/results/bcFiles/repairedFiles: 
    cd repair
    make -f makeRepair -B
```

Final Report will be saved in repair/Report.txt. This report contains stats for repair of DURA, MPB, and MPA bugs for all micro and real world benchmarks. The tables 1 and 2 from the paper can be generated from Report.txt by running the following command:
```
# Results will be saved in experiments/results_table1.csv and experiments/results_table2.csv: 
    cd experiments
    python3 convertResultsToCsv.py
```

## FAQs (May help in Setting up benchmarks)
### 1. Memcached: [memcached_pmem](https://github.com/lenovo/memcached-pmem)
#### Steps taken to install:
```
# Install memcached client
    sudo apt install libmemcached-dev
            
# Simulate PMEM on Emperor: /dev/loop40 will act as pmem device
    dd if=/dev/zero of=/dev/shm/pmem_sim.img bs=1M count=2048
    sudo losetup /dev/loop40 /dev/shm/pmem_sim.img
    sudo mkfs -t ext4 /dev/loop40
    sudo mount /dev/loop40 /mnt/pmfs

# Install memcached server using default settings
    ./configure --enable-pslab
    make
    sudo make install

# Install memcached server with custom compilation designed for LLVM OPT pass
    ./configure --enable-pslab
    ./customCompilation
```

#### Steps to run:
```
# Begin memcached server
    sudo memcached -u root -o pslab_file=/mnt/pmfs/pool,pslab_force
            
# Compile the code "example.c" with:
    gcc -o example example.c -lmemcached

# Run the "example" executable with:
    ./example
```
