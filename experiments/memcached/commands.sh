

PMInvGen_DIR=../../build/Transform

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG   -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls  -MT memcached-memcached.o -MD -MP -MF memcached-memcached.Tpo -c -emit-llvm  -o memcached_test.bc memcached.c -I$PMInvGen_DIR/../../Transform/PM -O0  
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen memcached_test.bc -o memcached_trace.bc
mv -f memcached-memcached.Tpo memcached-memcached.Po


#clang -g -O0 -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-memcached.o -MD -MP -MF memcached-memcached.Tpo -c -o memcached-memcached.o `test -f 'memcached.c' || echo './'`memcached.c
mv -f memcached-memcached.Tpo memcached-memcached.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-hash.o -MD -MP -MF memcached-hash.Tpo -c -o memcached-hash.o `test -f 'hash.c' || echo './'`hash.c
mv -f memcached-hash.Tpo memcached-hash.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-jenkins_hash.o -MD -MP -MF memcached-jenkins_hash.Tpo -c -o memcached-jenkins_hash.o `test -f 'jenkins_hash.c' || echo './'`jenkins_hash.c
mv -f memcached-jenkins_hash.Tpo memcached-jenkins_hash.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-murmur3_hash.o -MD -MP -MF memcached-murmur3_hash.Tpo -c -o memcached-murmur3_hash.o `test -f 'murmur3_hash.c' || echo './'`murmur3_hash.c
mv -f memcached-murmur3_hash.Tpo memcached-murmur3_hash.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG   -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls  -MT memcached-slabs.o -MD -MP -MF memcached-slabs.Tpo -c -emit-llvm   -o slabs_test.bc slabs.c -I$PMInvGen_DIR/../../Transform/PM -O0  
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen slabs_test.bc -o slabs_trace.bc
mv -f memcached-slabs.Tpo memcached-slabs.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG   -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls  -MT memcached-items.o -MD -MP -MF memcached-items.Tpo -c -emit-llvm   -o items_test.bc items.c -I$PMInvGen_DIR/../../Transform/PM -O0  
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen items_test.bc -o items_trace.bc
mv -f memcached-items.Tpo memcached-items.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-assoc.o -MD -MP -MF memcached-assoc.Tpo -c -o memcached-assoc.o `test -f 'assoc.c' || echo './'`assoc.c
mv -f memcached-assoc.Tpo memcached-assoc.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-thread.o -MD -MP -MF memcached-thread.Tpo -c -o memcached-thread.o `test -f 'thread.c' || echo './'`thread.c
mv -f memcached-thread.Tpo memcached-thread.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-daemon.o -MD -MP -MF memcached-daemon.Tpo -c -o memcached-daemon.o `test -f 'daemon.c' || echo './'`daemon.c
mv -f memcached-daemon.Tpo memcached-daemon.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-stats.o -MD -MP -MF memcached-stats.Tpo -c -o memcached-stats.o `test -f 'stats.c' || echo './'`stats.c
mv -f memcached-stats.Tpo memcached-stats.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-util.o -MD -MP -MF memcached-util.Tpo -c -o memcached-util.o `test -f 'util.c' || echo './'`util.c
mv -f memcached-util.Tpo memcached-util.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-bipbuffer.o -MD -MP -MF memcached-bipbuffer.Tpo -c -o memcached-bipbuffer.o `test -f 'bipbuffer.c' || echo './'`bipbuffer.c
mv -f memcached-bipbuffer.Tpo memcached-bipbuffer.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-logger.o -MD -MP -MF memcached-logger.Tpo -c -o memcached-logger.o `test -f 'logger.c' || echo './'`logger.c
mv -f memcached-logger.Tpo memcached-logger.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-crawler.o -MD -MP -MF memcached-crawler.Tpo -c -o memcached-crawler.o `test -f 'crawler.c' || echo './'`crawler.c
mv -f memcached-crawler.Tpo memcached-crawler.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-itoa_ljust.o -MD -MP -MF memcached-itoa_ljust.Tpo -c -o memcached-itoa_ljust.o `test -f 'itoa_ljust.c' || echo './'`itoa_ljust.c
mv -f memcached-itoa_ljust.Tpo memcached-itoa_ljust.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-slab_automove.o -MD -MP -MF memcached-slab_automove.Tpo -c -o memcached-slab_automove.o `test -f 'slab_automove.c' || echo './'`slab_automove.c
mv -f memcached-slab_automove.Tpo memcached-slab_automove.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-cache.o -MD -MP -MF memcached-cache.Tpo -c -o memcached-cache.o `test -f 'cache.c' || echo './'`cache.c
mv -f memcached-cache.Tpo memcached-cache.Po

clang -g -O0 -DPSLAB -DHAVE_CONFIG_H -I /home/toobak/PMBugRepair/Transform/PM/ -I.  -DNDEBUG -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -emit-llvm -MT memcached-pslab.o -MD -MP -MF memcached-pslab.Tpo   -c pslab.c -o pslab_test.bc -fPIE -I$PMInvGen_DIR/../../Transform/PM -O0
opt -load $PMInvGen_DIR/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen pslab_test.bc -o pslab_trace.bc
mv -f memcached-pslab.Tpo memcached-pslab.Po

clang -g -O0 -DPSLAB -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -o memcached memcached_trace.bc memcached-hash.o memcached-jenkins_hash.o memcached-murmur3_hash.o slabs_trace.bc items_trace.bc memcached-assoc.o memcached-thread.o memcached-daemon.o memcached-stats.o memcached-util.o memcached-bipbuffer.o memcached-logger.o memcached-crawler.o memcached-itoa_ljust.o memcached-slab_automove.o memcached-cache.o pslab_trace.bc  -levent -lpthread -lstdc++ -lrt -lm -L$PMInvGen_DIR/PM  -Wl,-rpath=$PMInvGen_DIR/PM -lLLVMPMC  -lpmemobj -lpmem -lpthread

rm *.o *.bc *.Po
