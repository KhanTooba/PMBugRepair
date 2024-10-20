
rm output.txt cleanOutput.txt

PMInvGen_DIR=../../../PMBugRepair/build/Transform

clang++-10 -g -std=c++11 -emit-llvm -c src/test.cpp -o test.bc -I$PMInvGen_DIR/../../Transform/PM -O0

opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen test.bc -o test_trace.bc
clang++-10 -g -o btree_concurrent_mixed test_trace.bc -L$PMInvGen_DIR/PM -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC -O0 -lrt -lm -pthread -lpmemobj -DCONCURRENT -DMIXED

#########################################################################
# Step-4 Run the final executable and delete all .bc files
#########################################################################
sudo rm /mnt/pmfs/pool6
sudo ./btree_concurrent_mixed -n 140 -i input.txt -t 2 -p /mnt/pmfs/pool6
rm *.bc *.ll a.out

mv output.txt ../../results/outputs/fastFair_output.txt
