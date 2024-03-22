#include <iostream>
#include <thread>
#include "pm.h"

// Overridden operator new function
void *operator new(size_t size) {
    void *ret;
    ret = pmalloc(size);
    return ret;
}
// int *x;
// int *y;

int main() {
    int *x = new int;
    int *y = new int;
    *x = 10;
    *y = *x;
    
    return 0;
}
