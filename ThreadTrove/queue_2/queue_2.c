#include <queue_2.h>

int main() {
    pthread_t thread1, thread2;

    pthread_mutex_init(&queue_mutex, NULL);  

    for (int i = 0; i < 10; i++) {
        enqueue(i);
    }

    pthread_create(&thread1, NULL, thread_func, NULL);
    pthread_create(&thread2, NULL, thread_func, NULL);

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    pthread_mutex_destroy(&queue_mutex);

    return 0;
}
