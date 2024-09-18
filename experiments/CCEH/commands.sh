rm output.txt output_clean.txt
PMInvGen_DIR=../../../PMBugRepair/build/Transform

#clang++-10 -O3 -std=c++17 -I./ -lrt -c -o src/CCEH.o src/CCEH.cpp -DINPLACE -lpmemobj -lpmem
clang++-10 -g -O3 -std=c++17 -I./ -lrt -emit-llvm -c -o src/CCEH.bc src/CCEH.cpp -DINPLACE -lpmemobj -lpmem -I$PMInvGen_DIR/../../Transform/PM -O0 -I./ -DMULTITHREAD
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  src/CCEH.bc -o src/CCEH_trace.bc


clang++-10 -g -I./include -std=c++11 -emit-llvm -c src/test.cpp -o src/test.bc -I$PMInvGen_DIR/../../Transform/PM -O0 -I./ -lpmemobj -lpmem -DMULTITHREAD
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  src/test.bc -o src/test_trace.bc

clang++-10 -g -std=c++17 -I./ -lrt -lpthread -O3 -o bin/multi_threaded_cceh src/test_trace.bc src/CCEH_trace.bc -lpmemobj -lpmem -lpthread -DMULTITHREAD -I$PMInvGen_DIR/../../Transform/PM -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC  -O0

sudo rm /mnt/pmfs/pool1
sudo ./bin/multi_threaded_cceh /mnt/pmfs/pool1 10 2
python3 cleanOutput.py output.txt output_clean.txt
cp output_clean.txt ../../results/outputs/CCEH_output.txt
rm output.txt
