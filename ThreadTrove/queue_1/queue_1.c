#include <queue_1.h>

void* thread_func() {
    int start = rand();
    for (int i = start; i < start + 25; i++) {
        enqueue(i);
        printf("Enqueued: %d\n", i);
    }

    for (int i = 0; i < 25; i++) {
        int dequeued_value = dequeue();
        if (dequeued_value != -1) {
            printf("Dequeued: %d\n", dequeued_value);
        } else {
            printf("Queue is empty\n");
        }
    }

    return NULL;
}

int main() {
    pthread_t thread1, thread2;

    pthread_mutex_init(&queue_mutex, NULL);  

    pthread_create(&thread1, NULL, thread_func, NULL);
    pthread_create(&thread2, NULL, thread_func, NULL);


    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    pthread_mutex_destroy(&queue_mutex);

    return 0;
}
