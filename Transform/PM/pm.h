#include <stdio.h>
#include <stdlib.h>
#include <libpmemobj.h>

#ifndef PM_INVARIANT_GENERATION_PM_H
#define PM_INVARIANT_GENERATION_PM_H

#ifdef __cplusplus
extern "C" {
#endif

  void __pmc_Initialize() ;

  void  *__pmc_malloc  (size_t size);
  void  *__pmc_calloc  (size_t blocks, size_t size);
  void  __pmc_free   (void *block);

//Tooba's addition:
  void __fence(int line, int col);
  void __flush(void* ptr, long int size, int line, int col);

  //void __pmc_memAdd(long long int k, long long int size) ;
  //void __pmc_memRemove(long long int k);
  //void __pmc_memClear();

  void __pmc_dummy_begin(int dummy);
  void __pmc_dummy_end(int dummy);
  void __pmc_funcBegin(const char* func);
  void __pmc_funcEndn(const char* func);

  void __pmc_depAdd(int ID1, int ID2) ;
  //void __pmc_printDep(int ID1, int ID2);
  //void __pmc_printCDep(int ID1, int ID2);
  //void __pmc_printDDep(int ID1, int ID2);
  
  void __pmc_printStoreAddr(long long int addr, int size, int ID, int Line, int Col, const char* scope);
  void __pmc_printLoadAddr(long long int addr, int size, int ID, int Line, int Col, const char* scope);
  int __pmc_pobj_alloc(PMEMobjpool *pop, PMEMoid *oidp, uint64_t type_num, size_t size, pmemobj_constr constructor, void *arg);
  PMEMobjpool* __pmc_pmemobj_create(const char *path, const char *layout, size_t poolsize, mode_t mode);
  PMEMobjpool* __pmc_pmemobj_open(const char *path, const char *layout);

  void simuSfence();
  void simuFlushOpt(void *ptr, long int len);
  void simuFlush(void *ptr, long int len);
  void simuTX_BEGIN();
  void simuTX_END();
  void simuTX_ADD(void *ptr);

#define pmalloc __pmc_malloc
#define pcalloc  __pmc_calloc
#define pfree     __pmc_free
// #define POBJ_ALLOC __pmc_pobj_alloc
#define PMEM_POBJ_ALLOC(pop, o, t, size, constr, arg) __pmc_pobj_alloc((pop), (PMEMoid *)(o), (size), TOID_TYPE_NUM(t), (constr), (arg))
#define pmemobj_create __pmc_pmemobj_create
#define pmemonj_open __pmc_pmemobj_open
#ifdef __cplusplus
}
#endif

#endif //PM_INVARIANT_GENERATION_PM_H
