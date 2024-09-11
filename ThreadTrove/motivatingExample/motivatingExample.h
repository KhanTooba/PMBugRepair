#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

typedef struct {
    int *x;
    int *y;
} PersistentMemory;

void PersistentMemory_init(PersistentMemory *pm) {
    pm->x = (int*) pmalloc(sizeof(int));
    pm->y = (int*) pmalloc(sizeof(int));
}

void* thread1_function(void *arg) {
    PersistentMemory *pm = (PersistentMemory*) arg;
    *(pm->x) = 10;
    return NULL;
}

void* thread2_function(void *arg) {
    PersistentMemory *pm = (PersistentMemory*) arg;
    *(pm->y) = *(pm->x);
    simuFlushOpt(pm->y, (int) sizeof(*(pm->y)));
    simuSfence();
    return NULL;
}