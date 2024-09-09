#include<set.h>
#define N_THREADS 2

// Thread function simulating write-after-write dependency
void* thread_func(void* arg) {
    Set* set = (Set*)arg;
    
    // Thread will remove an element, modify it, and reinsert it
    for (int i = 0; i < 5; i++) {
        int element = i;
        set_remove(set, element);        // Remove element
        element += 10;                   // Modify element
        set_insert(set, element);        // Reinsert element with modification
    }

    return NULL;
}

int main() {
    Set set;
    set_init(&set);

    // Initial insertions
    for (int i = 0; i < 10; i++) {
        set_insert(&set, i);
    }

    // Create threads
    pthread_t threads[N_THREADS];

    for (int i = 0; i < N_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_func, (void*)&set);
    }

    // Wait for threads to finish
    for (int i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Print the final set
    set_print(&set);

    // Clean up
    set_destroy(&set);

    return 0;
}
