gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-memcached.o -MD -MP -MF .deps/memcached-memcached.Tpo -c -o memcached-memcached.o `test -f 'memcached.c' || echo './'`memcached.c
mv -f .deps/memcached-memcached.Tpo .deps/memcached-memcached.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-hash.o -MD -MP -MF .deps/memcached-hash.Tpo -c -o memcached-hash.o `test -f 'hash.c' || echo './'`hash.c
mv -f .deps/memcached-hash.Tpo .deps/memcached-hash.Po

clang -g -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-jenkins_hash.o -MD -MP -MF .deps/memcached-jenkins_hash.Tpo -c -o memcached-jenkins_hash.o `test -f 'jenkins_hash.c' || echo './'`jenkins_hash.c
mv -f .deps/memcached-jenkins_hash.Tpo .deps/memcached-jenkins_hash.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-murmur3_hash.o -MD -MP -MF .deps/memcached-murmur3_hash.Tpo -c -o memcached-murmur3_hash.o `test -f 'murmur3_hash.c' || echo './'`murmur3_hash.c
mv -f .deps/memcached-murmur3_hash.Tpo .deps/memcached-murmur3_hash.Po

clang -g -DHAVE_CONFIG_H -I.  -DNDEBUG   -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls  -MT memcached-slabs.o -MD -MP -MF .deps/memcached-slabs.Tpo -c -emit-llvm -o slabs_test.bc slabs.c -I../PMBugRepair/build/Transform/../../Transform/PM -O0
opt -load ../PMBugRepair/build/Transform/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen slabs_test.bc -o slabs_trace.bc
llc-10 -filetype=obj slabs_trace.bc -o slabs.o
mv -f .deps/memcached-slabs.Tpo .deps/memcached-slabs.Po

clang -g -DHAVE_CONFIG_H -I.  -DNDEBUG   -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls  -MT memcached-items.o -MD -MP -MF .deps/memcached-items.Tpo -c -emit-llvm -o items_test.bc items.c -I../PMBugRepair/build/Transform/../../Transform/PM -O0
opt -load ../PMBugRepair/build/Transform/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen items_test.bc -o items_trace.bc
llc-10 -filetype=obj items_trace.bc -o items.o
mv -f .deps/memcached-items.Tpo .deps/memcached-items.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-assoc.o -MD -MP -MF .deps/memcached-assoc.Tpo -c -o memcached-assoc.o `test -f 'assoc.c' || echo './'`assoc.c
mv -f .deps/memcached-assoc.Tpo .deps/memcached-assoc.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-thread.o -MD -MP -MF .deps/memcached-thread.Tpo -c -o memcached-thread.o `test -f 'thread.c' || echo './'`thread.c
mv -f .deps/memcached-thread.Tpo .deps/memcached-thread.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-daemon.o -MD -MP -MF .deps/memcached-daemon.Tpo -c -o memcached-daemon.o `test -f 'daemon.c' || echo './'`daemon.c
mv -f .deps/memcached-daemon.Tpo .deps/memcached-daemon.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-stats.o -MD -MP -MF .deps/memcached-stats.Tpo -c -o memcached-stats.o `test -f 'stats.c' || echo './'`stats.c
mv -f .deps/memcached-stats.Tpo .deps/memcached-stats.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-util.o -MD -MP -MF .deps/memcached-util.Tpo -c -o memcached-util.o `test -f 'util.c' || echo './'`util.c
mv -f .deps/memcached-util.Tpo .deps/memcached-util.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-bipbuffer.o -MD -MP -MF .deps/memcached-bipbuffer.Tpo -c -o memcached-bipbuffer.o `test -f 'bipbuffer.c' || echo './'`bipbuffer.c
mv -f .deps/memcached-bipbuffer.Tpo .deps/memcached-bipbuffer.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-logger.o -MD -MP -MF .deps/memcached-logger.Tpo -c -o memcached-logger.o `test -f 'logger.c' || echo './'`logger.c
mv -f .deps/memcached-logger.Tpo .deps/memcached-logger.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-crawler.o -MD -MP -MF .deps/memcached-crawler.Tpo -c -o memcached-crawler.o `test -f 'crawler.c' || echo './'`crawler.c
mv -f .deps/memcached-crawler.Tpo .deps/memcached-crawler.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-itoa_ljust.o -MD -MP -MF .deps/memcached-itoa_ljust.Tpo -c -o memcached-itoa_ljust.o `test -f 'itoa_ljust.c' || echo './'`itoa_ljust.c
mv -f .deps/memcached-itoa_ljust.Tpo .deps/memcached-itoa_ljust.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-slab_automove.o -MD -MP -MF .deps/memcached-slab_automove.Tpo -c -o memcached-slab_automove.o `test -f 'slab_automove.c' || echo './'`slab_automove.c
mv -f .deps/memcached-slab_automove.Tpo .deps/memcached-slab_automove.Po

gcc -DHAVE_CONFIG_H -I.  -DNDEBUG    -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT memcached-cache.o -MD -MP -MF .deps/memcached-cache.Tpo -c -o memcached-cache.o `test -f 'cache.c' || echo './'`cache.c
mv -f .deps/memcached-cache.Tpo .deps/memcached-cache.Po

clang -g -DHAVE_CONFIG_H -I /home/toobak/PMBugRepair/Transform/PM/ -I.  -DNDEBUG -pthread -pthread -Wall  -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -emit-llvm -MT memcached-pslab.o -MD -MP -MF .deps/memcached-pslab.Tpo -c pslab.c -o pslab_test.bc -fPIE -I../PMBugRepair/build/Transform/../../Transform/PM -O0
opt -load ../PMBugRepair/build/Transform/PMTraceGen/libLLVMPMTraceGen.so --pmtracegen pslab_test.bc -o pslab_trace.bc
llc-10 -filetype=obj pslab_trace.bc -o pslab.o
mv -f .deps/memcached-pslab.Tpo .deps/memcached-pslab.Po

clang -g  -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls   -o memcached memcached-memcached.o memcached-hash.o memcached-jenkins_hash.o memcached-murmur3_hash.o slabs.o items.o memcached-assoc.o memcached-thread.o memcached-daemon.o memcached-stats.o memcached-util.o memcached-bipbuffer.o memcached-logger.o memcached-crawler.o memcached-itoa_ljust.o memcached-slab_automove.o memcached-cache.o pslab.o   -lpmem -levent -lpthread -lstdc++ -lrt -lm -L../PMBugRepair/build/Transform/PM  -Wl,-rpath=../PMBugRepair/build/Transform/PM -lLLVMPMC  -lpmemobj -lpmem -lpthread



gcc -DHAVE_CONFIG_H -I.      -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT sizes.o -MD -MP -MF .deps/sizes.Tpo -c -o sizes.o sizes.c
mv -f .deps/sizes.Tpo .deps/sizes.Po

gcc   -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls   -o sizes sizes.o  -levent 
gcc -DHAVE_CONFIG_H -I.      -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT testapp.o -MD -MP -MF .deps/testapp.Tpo -c -o testapp.o testapp.c
mv -f .deps/testapp.Tpo .deps/testapp.Po

gcc -DHAVE_CONFIG_H -I.      -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT util.o -MD -MP -MF .deps/util.Tpo -c -o util.o util.c
mv -f .deps/util.Tpo .deps/util.Po

gcc -DHAVE_CONFIG_H -I.      -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT cache.o -MD -MP -MF .deps/cache.Tpo -c -o cache.o cache.c
mv -f .deps/cache.Tpo .deps/cache.Po

gcc   -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls   -o testapp testapp.o util.o cache.o  -levent 

gcc -DHAVE_CONFIG_H -I.      -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls -MT timedrun.o -MD -MP -MF .deps/timedrun.Tpo -c -o timedrun.o timedrun.c
mv -f .deps/timedrun.Tpo .deps/timedrun.Po

gcc   -pthread -pthread -Wall -Werror -pedantic -Wmissing-prototypes -Wmissing-declarations -Wredundant-decls   -o timedrun timedrun.o  -levent -lpmemobj -lpmem -lpthread
