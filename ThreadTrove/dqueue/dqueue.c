#include <dqueue.h>

#define N_THREADS 2

// Thread function to introduce write-after-write dependency
void* thread_func(void* arg) {
    Deque* deque = (Deque*)arg;

    // Thread performs multiple operations on the deque
    for(int i=0; i<50; i++){
        int value = deque_pop_front(deque);
        deque_push_back(deque, value + 1);
        deque_push_front(deque, value + 2);
        deque_pop_back(deque);
    }

    return NULL;
}

int main() {
    Deque deque;
    deque_init(&deque);

    // Insert initial values
    for(int i=0; i<100; i++){
        deque_push_back(&deque, rand());
    }

    pthread_t threads[N_THREADS];

    // Create threads
    for (int i = 0; i < N_THREADS; ++i) {
        pthread_create(&threads[i], NULL, thread_func, (void*)&deque);
    }

    // Wait for threads to finish
    for (int i = 0; i < N_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Print final state of the deque
    deque_print(&deque);

    deque_destroy(&deque);
    return 0;
}
