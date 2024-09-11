#!/bin/bash
##### automatically set up PMInvGen_DIR ####
PMInvGen_DIR=../../build/Transform

#PMInvGen_DIR=/home/rss/src/PMC/build/Transform

#########################################################################
# Step-1  Compiling (Program-Under-Test) to *.bc
#########################################################################
clang++-10 -g  -I./include  -std=c++11  -emit-llvm   -c test.cpp -o test.bc      -I$PMInvGen_DIR/../../Transform/PM -O0

#########################################################################
# Step-2  opt --pmtracegen
#########################################################################
echo "opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen   test.bc -o test_trace.bc"
opt           -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen   test.bc -o test_trace.bc

#########################################################################
# Step-3  Linking  (Program-Under-Test) with (Zunchen's Library) 
#########################################################################
clang++-10 -g  test_trace.bc  -lstdc++ -lrt -lm -lpthread     -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC  -O0


llvm-dis test.bc
llvm-dis test_trace.bc

