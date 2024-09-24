
g++ -c -I include -I external/include -I src -std=c++17 -march=native -mrtm -mcx16 -mavx -mavx2 -mbmi2 -mlzcnt example.cpp -o example.o

gcc -c -I include -I external/include src/clht_gc.c -o clht_gc.o

gcc -c -I include -I external/include src/clht_lb_res.c -o clht_lb_res.o

gcc -c external/sspfd/sspfd.c -o sspfd.o

gcc -c -I external/ssmem/include external/ssmem/src/ssmem.c -o ssmem.o

g++ example.o clht_gc.o clht_lb_res.o sspfd.o ssmem.o -o example_executable -lboost_system -lboost_thread -ltbb -ljemalloc -lpthread

rm *.o
