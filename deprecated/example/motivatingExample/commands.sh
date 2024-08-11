#!/bin/bash
##### automatically set up PMInvGen_DIR ####
PMInvGen_DIR=$(dirname "$0")/../../build/Transform


#########################################################################
# Step-1  Compiling (Program-Under-Test) to *.bc
#########################################################################
clang++-10 -g  -I./include  -std=c++11  -emit-llvm   -c toy.cpp -o toy.bc      -I$PMInvGen_DIR/../../Transform/PM

#########################################################################
# Step-2  opt --pmtracegen
#########################################################################
echo "opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen   test.bc -o test_trace.bc"
opt           -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen   toy.bc -o toy_trace.bc

#########################################################################
# Step-3  Linking  (Program-Under-Test) with (Zunchen's Library) 
#########################################################################
clang++-10 -g  toy_trace.bc  -lstdc++ -lrt -lm -lpthread     -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC 


# llvm-dis test.bc
# llvm-dis test_trace.bc
