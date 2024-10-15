PMInvGen_DIR=../../../../../PMBugRepair/build/Transform
sudo rm output.txt codeOutput.txt

sudo rm clevel_hash_ycsb

#clang++-10 -g -c -emit-llvm ../../examples/doc_snippets/transaction.cpp -o transaction.bc -I../../include -I../../../PMBugRepair/Transform/PM
#opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  transaction.bc -o transaction_trace.bc

#clang++-10 -g -c -emit-llvm -O3 clevel_hash_ycsb.cpp  -I ../ -I../../include -I ../../include/libpmemobj++/transaction.hpp -I$PMInvGen_DIR/../../Transform/PM -o clevel_hash_ycsb.bc
clang++-10 -g -c -emit-llvm -O3 clevel_hash_ycsb.cpp  -I ../ -I../../include -I$PMInvGen_DIR/../../Transform/PM -o bcFiles/clevel_hash_ycsb.bc

opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  bcFiles/clevel_hash_ycsb.bc -o bcFiles/clevel_hash_ycsb_trace.bc

clang++-10 -g -std=c++17 -I./ -lrt -O3 -o clevel_hash_ycsb bcFiles/clevel_hash_ycsb_trace.bc -lpmemobj -lpmem -lpthread -I$PMInvGen_DIR/../../Transform/PM -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC -O0  -I transaction_trace.bc


sudo ./clevel_hash_ycsb /mnt/pmfs/pool4 input.txt output.txt 3 >> codeOutput.txt
sudo rm /mnt/pmfs/pool4
sudo rm .clevel_hash_ycsb.cpp.swp  
#sudo rm *.bc

#Files modified:
#1.concurrent_hash_map.hpp
#
#
#
