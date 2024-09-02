# PMBugRepair

## Ongoing work: Baseline version.

To build the trace generator llvm opt pass: 
```
# Build opt pass (Results will be saved in PMBugRepair/build): 
    sh builder.sh
```

To generate trace for all benchmarks in the benchmark folder: 
```
# Generate traces (Results will be saved in PMBugRepair/benchmark/bcFiles/outputs): 
    make -f benchmarkMake -s -B
```

To execute step1 (repair individual traces) for all benchmarks in the benchmark folder: 
```
# Execute step 1 (Results will be saved in PMBugRepair/benchmark/bcFiles/results): 
    cd repair
    make -f makeRepair -s -B
```

## Updates:
1. DURA, MPB and MPB bug repair has been added.
2. Results verified on programs under benchmark folder and FAST FAIR benchmark.
3. Results pending for the remaining ASPLOS benchmarks.


## Experimental Setup
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

# Install memcached server
    ./configure --enable-pslab
    make
    sudo make install
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

### 2. Redis: [redis](https://github.com/redis/redis)
#### Steps taken to install: