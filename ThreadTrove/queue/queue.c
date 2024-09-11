#include <queue.h>

// Thread function for concurrent queue operations
void* threadFunc(void* arg) {
    Queue* queue = (Queue*)arg;

    int start = rand();
    for (int i = start; i < start + 25; i++) {
        enqueue(queue, i);
        printf("Enqueued: %d\n", i);
    }

    for (int i = 0; i < 15; i++) {
        int dequeued_value = dequeue(queue);
        if (dequeued_value != -1) {
            printf("Dequeued: %d\n", dequeued_value);
        } else {
            printf("Queue is empty\n");
        }
        int data = front(queue);
    }
    
    printQueue(queue);

    return NULL;
}

int main() {
    // Create a queue
    Queue* queue = createQueue();

    // Create threads
    int n_threads = 2;
    pthread_t threads[n_threads];

    for (int i = 0; i < n_threads; ++i) {
        pthread_create(&threads[i], NULL, threadFunc, (void*)queue);
    }

    // Join threads
    for (int i = 0; i < n_threads; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Print the final state of the queue
    printf("Final state of the queue:\n");
    printQueue(queue);

    return 0;
}

