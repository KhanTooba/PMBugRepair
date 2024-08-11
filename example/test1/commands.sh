#!/bin/bash
##### automatically set up PMInvGen_DIR ####
PMInvGen_DIR=$(dirname "$0")/../../build/Transform

#PMInvGen_DIR=/home/rss/src/PMC/build/Transform

#########################################################################
# Step-1  Compiling (Program-Under-Test) to *.bc
#########################################################################
clang -g -I include  -emit-llvm -c  array_source.c -o  array_source.bc     -I$PMInvGen_DIR/../../Transform/PM
clang -g -I include  -emit-llvm -c  stack_source.c -o  stack_source.bc     -I$PMInvGen_DIR/../../Transform/PM
clang -g -I include  -emit-llvm -c test_on_stack.c -o test_on_stack.bc     -I$PMInvGen_DIR/../../Transform/PM


#########################################################################
# Step-2  opt --pmtracegen
#########################################################################
echo opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  array_source.bc  -o array_source_trace.bc
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  array_source.bc  -o array_source_trace.bc
echo opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  stack_source.bc  -o stack_source_trace.bc
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  stack_source.bc  -o stack_source_trace.bc
echo opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  test_on_stack.bc -o test_on_stack_trace.bc
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  test_on_stack.bc -o test_on_stack_trace.bc


#########################################################################
# Step-4  Linking  (Program-Under-Test) with (Zunchen's Library) 
#########################################################################
clang -g  array_source_trace.bc stack_source_trace.bc test_on_stack_trace.bc  -L/usr/lib/x86_64-linux-gnu -lstdc++ -lCppUTest -lCppUTestExt -lm       -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC 


llvm-dis  array_source.bc
llvm-dis  array_source_trace.bc
llvm-dis  stack_source.bc
llvm-dis  stack_source_trace.bc
llvm-dis  test_on_stack.bc
llvm-dis  test_on_stack_trace.bc

