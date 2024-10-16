##### REMOVING ALL OLD FILES
rm output.txt cleanOutput.txt

##### INSTRUMENTING CODE WITH OPT PASS
PMInvGen_DIR=../../PMBugRepair/build/Transform

#########################################################################
# Step-1  Compiling (Program-Under-Test) to *.bc
#########################################################################
clang++-10 -g -std=c++11 -emit-llvm -c src/test.cpp -o test.bc -I$PMInvGen_DIR/../../Transform/PM -O0

#########################################################################
# Step-2  opt --pmtracegen
#########################################################################
echo "opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen test.bc -o test_trace.bc"
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen test.bc -o test_trace.bc

#########################################################################
# Step-3  Linking  (Program-Under-Test) with (Zunchen's Library) 
#########################################################################
clang++-10 -g -o btree_concurrent_mixed test_trace.bc -L$PMInvGen_DIR/PM -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC -O0 -lrt -lm -pthread -lpmemobj -DCONCURRENT -DMIXED

#########################################################################
# Step-4 Run the final executable and delete all .bc files
#########################################################################
sudo rm /mnt/pmfs/pool6
sudo ./btree_concurrent_mixed -n 50 -i input.txt -t 4 -p /mnt/pmfs/pool6
rm *.bc *.ll a.out
