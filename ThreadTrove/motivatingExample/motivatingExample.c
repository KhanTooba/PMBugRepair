#include <example.h>

int main() {
    PersistentMemory pm;
    pthread_t t1, t2;

    PersistentMemory_init(&pm);

    // Create and run threads
    pthread_create(&t1, NULL, thread1_function, &pm);
    pthread_create(&t2, NULL, thread2_function, &pm);

    // Wait for threads to finish
    pthread_join(t1, NULL);
    pthread_join(t2, NULL);

    return 0;
}
