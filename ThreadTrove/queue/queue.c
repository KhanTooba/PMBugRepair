#include <queues.h>

int main() {
    pthread_t thread1, thread2;

    pthread_mutex_init(&queue_mutex, NULL); 

    int start = 0;
    pthread_create(&thread1, NULL, enqueue_thread_func, &start);
    pthread_create(&thread2, NULL, dequeue_thread_func, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    pthread_mutex_destroy(&queue_mutex);

    return 0;
}

