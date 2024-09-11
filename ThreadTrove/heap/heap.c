#include <stdio.h>
#include <pthread.h>
#include "heap.h"

#define N_THREADS 2

typedef struct {
    Heap *heap;
    int thread_id;
} ThreadData;

// Function for threads to run
void* threadFunction(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    Heap* heap = data->heap;
    int thread_id = data->thread_id;

    // Example of write-after-write dependency
    for(int i=0;i<25;i++){
        insertHeap(heap, rand());
    }

    if(!isEmpty(heap)){
        int min = extractMin(heap);
        insertHeap(heap, min);
    }

    printHeap(heap);
    pthread_exit(NULL);
}

int main() {
    Heap* heap = createHeap(10);

    pthread_t threads[N_THREADS];
    ThreadData thread_data[N_THREADS];

    // Create threads
    for (int i = 0; i < N_THREADS; i++) {
        thread_data[i].heap = heap;
        thread_data[i].thread_id = i;
        pthread_create(&threads[i], NULL, threadFunction, &thread_data[i]);
    }

    // Join threads
    for (int i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Example of write-after-write dependency in main
    insertHeap(heap, 5);
    insertHeap(heap, 0);

    printHeap(heap);

    destroyHeap(heap);
    return 0;
}
