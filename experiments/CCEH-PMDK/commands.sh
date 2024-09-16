PMInvGen_DIR=../../../PMBugRepair/build/Transform

#clang++-10 -O3 -std=c++17 -I./ -lrt -c -o src/CCEH.o src/CCEH.cpp -DINPLACE -lpmemobj -lpmem
clang++-10 -O3 -std=c++17 -I./ -lrt -c -o src/CCEH.o src/CCEH.cpp -DINPLACE -lpmemobj -lpmem -I$PMInvGen_DIR/../../Transform/PM -O0


clang++-10 -g -I./include -std=c++11 -emit-llvm -c src/test.cpp -o src/test.bc -I$PMInvGen_DIR/../../Transform/PM -O0 -I./
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  src/test.bc -o src/test_trace.bc

clang++-10 -std=c++17 -I./ -lrt -lpthread -O3 -o bin/multi_threaded_cceh src/test_trace.bc src/CCEH.o -lpmemobj -lpmem -lpthread -DMULTITHREAD -I$PMInvGen_DIR/../../Transform/PM -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC  -O0
