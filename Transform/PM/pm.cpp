#include <stdio.h>
#include <stdlib.h>
#include <map>
#include <set>
#include <thread>
#include <iostream>
#include <mutex>
#include <cstdio>
#include <cstdarg>
#include <pthread.h>
#include <string.h>

#include "pm.h"

#ifdef __cplusplus
extern "C" {
#endif

  static std::map<long long int, long long int> M;
  static std::map<const char*, unsigned> FUNC_STACK;
  static std::map<int, std::set<int>> DEP;
  static std::set<int> TRACE_IDS;
  
  static pthread_mutex_t mtx = PTHREAD_MUTEX_INITIALIZER;
  static pthread_mutex_t print = PTHREAD_MUTEX_INITIALIZER;
  
  static bool my_flag = false;  

void my_printf(const char* format, ...) {
    FILE *fptr;
    fptr = fopen("output.txt","a");
    if(fptr==NULL){
      printf("Could not open file.");
      return;
    }
    std::thread::id threadId = std::this_thread::get_id();
    size_t threadIdNum = std::hash<std::thread::id>{}(threadId);
    pthread_t tid = pthread_self();

    va_list args;
    va_start(args, format);
    {
      static char buffer [1024];
      vsnprintf(buffer, 1024, format, args);
      fprintf(fptr, "%s", buffer);
    }
    va_end(args);
    fprintf(fptr, "<Thread ID:%lu>\n", (unsigned long)tid);
    fclose(fptr);
}

  //------------------------------------------------------------------------------------------
  //  Functions to be instrumented by the LLVM opt pass
  //------------------------------------------------------------------------------------------

  void __pmc_Initialize() {
//printf("Came here");
    if (!my_flag) {
//	printf("Initializing variables\n");
      M = {};
      FUNC_STACK = {};
      DEP = {};
      TRACE_IDS = {};
      mtx = PTHREAD_MUTEX_INITIALIZER;
      my_flag = true;
    }
  }

void  *__pmc_malloc  (size_t size) {
  void *ptr = malloc(size);
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    //my_printf("Adding addr: 0x%llx; ", (unsigned long long)ptr);
    my_printf("Adding addr: 0x%llx to 0x%llx; ", (unsigned long long)ptr, (unsigned long long)ptr + size);
    M[(unsigned long long)ptr] = (unsigned long long)ptr + size;
    pthread_mutex_unlock(&mtx);
  }
  return ptr;
}

//Tooba's addition begins here:
void* __pmc_wrapper_pmem_map_file(const char *path, size_t len, int flags, mode_t mode, size_t *mapped_lenp, int *is_pmemp){
  void* pslab_pool = pmem_map_file(path, len, flags, mode, mapped_lenp, is_pmemp);
  pthread_mutex_lock(&mtx);

  unsigned long long start_addr_ull = (unsigned long long)pslab_pool;
  unsigned long long end_addr_ull = start_addr_ull + (unsigned long long)mapped_lenp;
        
  my_printf("Adding addr: 0x%llx to 0x%llx; ", start_addr_ull, end_addr_ull);

  M[start_addr_ull] = end_addr_ull;
  pthread_mutex_unlock(&mtx);
  return pslab_pool;
}
  

void __flush(void* ptr, long int size, int line, int col, const char* scope) {
  if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("CLFLUSH: %p LEN: %ld @Ln,Col: %d,%d ; Scope: %s;  ", ptr, size, line, col, scope);
      pthread_mutex_unlock(&mtx);
  }
}

void __fence(int line, int col, const char* scope){
  if (my_flag) {
    pthread_mutex_lock(&mtx);
	  my_printf("SFENCE. @Ln,Col: %d,%d ; Scope: %s;  ", line, col, scope);
    pthread_mutex_unlock(&mtx);
  }
}

int __pmc_pobj_alloc(PMEMobjpool *pop, PMEMoid *oidp, uint64_t type_num, size_t size, pmemobj_constr constructor, void *arg){
    int ret = pmemobj_alloc(pop, oidp, type_num, size, constructor, arg);
/**    if (my_flag && ret == 0) { 
        void *ptr = pmemobj_direct(*oidp); 
        pthread_mutex_lock(&mtx);

        unsigned long long start_addr_ull = (unsigned long long)ptr;
        unsigned long long end_addr_ull = start_addr_ull + size;
        
        my_printf("Adding addr: 0x%llx to 0x%llx; ", start_addr_ull, end_addr_ull);

        M[start_addr_ull] = end_addr_ull;
        pthread_mutex_unlock(&mtx);
    }*/
    return ret;  
}

PMEMobjpool* __pmc_pmemobj_create(const char *path, const char *layout, size_t poolsize, mode_t mode){
  PMEMobjpool* pop = pmemobj_create(path, layout, poolsize, mode);
  pthread_mutex_lock(&mtx);

  unsigned long long start_addr_ull = (unsigned long long)pop;
  unsigned long long end_addr_ull = start_addr_ull + poolsize;
        
  my_printf("Adding addr: 0x%llx to 0x%llx; ", start_addr_ull, end_addr_ull);

  M[start_addr_ull] = end_addr_ull;
  pthread_mutex_unlock(&mtx);
  return pop;
}

void pmem_create(unsigned long long pop, size_t poolsize)
{
  pthread_mutex_lock(&mtx);

  unsigned long long start_addr_ull = pop;
  unsigned long long end_addr_ull = start_addr_ull + poolsize;
        
  my_printf("Adding addr: 0x%llx to 0x%llx; ", start_addr_ull, end_addr_ull);

  M[start_addr_ull] = end_addr_ull;
  pthread_mutex_unlock(&mtx);
}

PMEMobjpool* __pmc_pmemobj_open(const char *path, const char *layout){
  PMEMobjpool* pop = pmemobj_open(path, layout);
  pthread_mutex_lock(&mtx);
  size_t pool_size;
  pmemobj_ctl_get(pop, "heap.size", &pool_size);

  unsigned long long start_addr_ull = (unsigned long long)pop;
  unsigned long long end_addr_ull = start_addr_ull + pool_size;
        
  my_printf("Adding addr: 0x%llx to 0x%llx; ", start_addr_ull, end_addr_ull);

  M[start_addr_ull] = end_addr_ull;
  pthread_mutex_unlock(&mtx);

  return pop;
}

void __transactionBegins(int Line, int Col, const char* scope){
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("Transaction begins. @Ln,Col: %d,%d Scope: %s; ", Line, Col, scope);
      pthread_mutex_unlock(&mtx);
    }
}

void __transactionCommits(int Line, int Col, const char* scope){
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("Transaction Commits. @Ln,Col: %d,%d Scope: %s; ", Line, Col, scope);
      pthread_mutex_unlock(&mtx);
    }
}

//Tooba's addition ends here.

void  *__pmc_calloc  (size_t blocks, size_t size) {
  void *ptr  = calloc(blocks, size);
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("Adding addr: 0x%llx to 0x%llx; ", (unsigned long long)ptr, (unsigned long long)ptr + size);
    M[(unsigned long long)ptr] = (unsigned long long)ptr + size;
    pthread_mutex_unlock(&mtx);
  }
  return ptr;
}

void  __pmc_free  (void *block) {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("Adding addr: 0x%llx; ", (unsigned long long)block);
    M.erase((unsigned long long)block);
    pthread_mutex_unlock(&mtx);
  }
  free(block);
}

  /*
void __pmc_memAdd(long long int k, long long int size) {
  if (my_flag) {  
    pthread_mutex_lock(&mtx);
    my_printf("Adding addr: 0x%llx to 0x%llx; ", k, k + size);
    M[k] = k + size;
    pthread_mutex_unlock(&mtx);
  }
}
void __pmc_memRemove(long long int k) {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("Removing addr: 0x%llx; ", k);
    M.erase(k);
   pthread_mutex_unlock(&mtx);
  }
}

void __pmc_memClear() {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    M.clear();
    pthread_mutex_unlock(&mtx);
  }
}
  */
  void __pmc_dummy_begin(int dummy) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      //do nothing
      pthread_mutex_unlock(&mtx);
    }
  }
  
  void __pmc_dummy_end(int dummy) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      // do nothing
      pthread_mutex_unlock(&mtx);
    }
  }

  void __pmc_funcBegin(const char* func) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      if (!FUNC_STACK.count(func)) {
        FUNC_STACK[func] = 1;
      }
      my_printf("FUNC_BEGIN_1: %s %u; ", func, FUNC_STACK[func]);
      pthread_mutex_unlock(&mtx);
    }
  }

  void __pmc_funcEnd(const char* func) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("FUNC_END: %s %u; ", func, FUNC_STACK[func]);
      FUNC_STACK[func]++;
      pthread_mutex_unlock(&mtx);
    }
  }
  
  void __pmc_depAdd(int ID1, int ID2) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      DEP[ID1].insert(ID2);
      pthread_mutex_unlock(&mtx);
    }
  }
  /*
  void __pmc_printDep(int ID1, int ID2) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("DEP: SrcID: %d DestID: %d; ", ID1, ID2);
      pthread_mutex_unlock(&mtx);
    }
  }

  void __pmc_printDDep(int ID1, int ID2) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("DDEP: SrcID: %d DestID: %d; ", ID1, ID2);
      pthread_mutex_unlock(&mtx);
    }
  }

  void __pmc_printCDep(int ID1, int ID2) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("CDEP: SrcID: %d DestID: %d; ", ID1, ID2);
      pthread_mutex_unlock(&mtx);
    }
  }
  */

  void __pmc_printStoreAddr(long long int addr, int size, int ID, int Line, int Col, const char* scope) {
	// my_printf("Store: Entering for 0x%llx: ", addr);
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      for (const auto &pair: M) {
        if (addr >= pair.first && addr + size <= pair.second) {
            TRACE_IDS.insert(ID);
            my_printf("Store: 0x%llx Size: %d ID: %d @Ln,Col: %d,%d Scope: %s; ", addr, size, ID, Line, Col, scope);
            for (const auto &p: DEP) {
                if (!TRACE_IDS.count(p.first)) continue;
                for (auto const& dep : p.second) {
                    if (dep == ID) {
		                  my_printf("DEP: SrcID: %d DestID: %d; ", p.first, dep);
                    }
                }
            }
        }
      }
      pthread_mutex_unlock(&mtx);
    }// if(my_flag)
  }

  void __pmc_printLoadAddr(long long int addr, int size, int ID, int Line, int Col, const char* scope) {
    if (my_flag) {
      pthread_mutex_lock(&mtx);
      for (const auto &pair: M) {
        if (addr >= pair.first && addr + size <= pair.second) {
	  TRACE_IDS.insert(ID);
	  my_printf("Load: 0x%llx Size: %d ID: %d @Ln,Col: %d,%d Scope: %s; ", addr, size, ID, Line, Col, scope);
	  for (const auto &p: DEP) {
	    if (!TRACE_IDS.count(p.first)) continue;
	    for (auto const& dep : p.second) {
	      if (dep == ID) {
		my_printf("DEP: SrcID: %d DestID: %d; ", p.first, dep);
	      }
	    }
	  }
        }
      }
      pthread_mutex_unlock(&mtx);
    }//    if (my_flag) {
  }

  //--------------------------------------------------------------------------------------------------------
  //  manually inserted to the program-under test
  //--------------------------------------------------------------------------------------------------------
void simuSfence() {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("Simulated F-E-N-C-E;");
    pthread_mutex_unlock(&mtx);
  }
}

void simuFlushOpt(void* ptr, long int len) {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("Simulated F-L-U-S-H: %p LEN: %ld; ", ptr, len);
    pthread_mutex_unlock(&mtx);
  }
}

void simuFlush(void* ptr, long int len) {
  if (my_flag) {
      pthread_mutex_lock(&mtx);
      my_printf("Simulated F-L-U-S-H: %p LEN: %ld; ", ptr, len);
      pthread_mutex_unlock(&mtx);
  }
}

void simuTX_BEGIN() {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("TX_BEGIN; ");
    pthread_mutex_unlock(&mtx);
  }
}

void simuTX_END() {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("TX_END; ");
    pthread_mutex_unlock(&mtx);
  }
}
  
void simuTX_ADD(void* ptr) {
  if (my_flag) {
    pthread_mutex_lock(&mtx);
    my_printf("TX_ADD: %p; ", ptr);
    pthread_mutex_unlock(&mtx);
  }
}
   
#ifdef __cplusplus
}
#endif
