#include<priorityQueue.h>
#define N_THREADS 2

// Thread function to perform priority queue operations with write-after-write dependency
void* thread_func(void* arg) {
    PriorityQueue* pq = (PriorityQueue*)arg;
    int value;

    for(int i=0;i<30;i++) {  
        value = rand()%10;
        pq_insert(pq, value, value);
    }

    value = pq_extract_min(pq);  // Extract minimum element
    return NULL;
}

int main() {
    PriorityQueue pq;
    pthread_t threads[N_THREADS];

    // Initialize the priority queue
    pq_init(&pq);

    // Insert some initial values
    pq_insert(&pq, 15, 15);
    pq_insert(&pq, 5, 5);
    pq_insert(&pq, 30, 30);

    // Create threads to perform operations with a write-after-write dependency
    for (int i = 0; i < N_THREADS; ++i) {
        pthread_create(&threads[i], NULL, thread_func, (void*)&pq);
    }

    // Wait for all threads to complete
    for (int i = 0; i < N_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Final priority queue state
    printf("Final priority queue size: %d\n", pq_size(&pq));
    while (!pq_is_empty(&pq)) {
        printf("%d\n", pq_extract_min(&pq));
    }

    // Destroy the priority queue
    pq_destroy(&pq);

    return 0;
}