#include <iostream>
#include <thread>
#include "pm.h"

void *operator new(size_t size) {
    void *ret;
    ret = pmalloc(size);
    return ret;
}

class PersistentMemory {
private:
    int *x;
    int *y;

public:
    PersistentMemory() {
        x = new int;
        y = new int;
    }

    void thread1_function() {
        *x = 10;
    }

    void thread2_function() {
        *y = *x;
    }
};

int main() {
    PersistentMemory pm;
    std::thread t1(&PersistentMemory::thread1_function, &pm)
    std::thread t2(&PersistentMemory::thread2_function, &pm);

    t1.join();
    t2.join();

    return 0;
}
