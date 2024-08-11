#include <example.h>

int main() {
    PersistentMemory pm;
    std::thread t1(&PersistentMemory::thread1_function, &pm);
    std::thread t2(&PersistentMemory::thread2_function, &pm);

    t1.join();
    t2.join();

    return 0;
}