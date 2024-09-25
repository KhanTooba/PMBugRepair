
rm output.txt

clang++-10 -g -O3 -lrt -emit-llvm -c -I include -I external/include -I src -std=c++17 -march=native -mrtm -mcx16 -mavx -mavx2 -mbmi2 -mlzcnt example.cpp -o example.bc -I../../../PMBugRepair/build/Transform/../../Transform/PM -O0 -I./ -fheinous-gnu-extensions
opt -load ../../../PMBugRepair/build/Transform/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  example.bc -o example_trace.bc


clang-10 -g -O3 -lrt -emit-llvm -c -I include -I external/include src/clht_gc.c -o clht_gc.bc -I../../../PMBugRepair/build/Transform/../../Transform/PM -O0 -I./ -fheinous-gnu-extensions
opt -load ../../../PMBugRepair/build/Transform/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  clht_gc.bc -o clht_gc_trace.bc

clang-10 -g -O3 -lrt -emit-llvm  -c -I include -I external/include src/clht_lb_res.c -o clht_lb_res.bc -I../../../PMBugRepair/build/Transform/../../Transform/PM -O0 -I./ -fheinous-gnu-extensions
opt -load ../../../PMBugRepair/build/Transform/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen  clht_lb_res.bc -o clht_lb_res_trace.bc


clang-10 -g -c external/sspfd/sspfd.c -o sspfd.o

clang-10 -g -c -I external/ssmem/include external/ssmem/src/ssmem.c -o ssmem.o

clang++-10 -g example_trace.bc clht_gc_trace.bc clht_lb_res_trace.bc sspfd.o ssmem.o -o example_executable -lboost_system -lboost_thread -ltbb -ljemalloc -lpthread -I../../../PMBugRepair/build/Transform/../../Transform/PM -L../../../PMBugRepair/build/Transform/PM  -Wl,-rpath=../../../PMBugRepair/build/Transform/PM -lLLVMPMC  -O0 -lpmemobj -lpmem


rm *.bc *.o *.ll

./example_executable 100 2

cp output.txt ../../results/outputs/P-CLHT_output.txt


