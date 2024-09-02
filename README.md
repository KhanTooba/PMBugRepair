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


## Experimental Setup
### Steps taken to install memcached:
```
# Install memcached client
    sudo apt install libmemcached-dev
            
# Simulate PMEM on Emperor: /dev/loop40 will act as pmem device
    dd if=/dev/zero of=/dev/shm/pmem_sim.img bs=1M count=2048
    sudo losetup /dev/loop40 /dev/shm/pmem_sim.img
    sudo mkfs -t ext4 /dev/loop40
    sudo mount /dev/loop40 /mnt/pmfs
```

### Steps to run memcached:
```
# Begin memcached server
    sudo memcached -u root -o pslab_file=/mnt/pmfs/pool,pslab_force
            
# Compile the code "example.c" with:
    gcc -o example example.c -lmemcached

# Run the "example" executable with:
    ./example
```
