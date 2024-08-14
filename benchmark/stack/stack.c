#include <stacks.h>
int main() {
    pthread_t thread1, thread2;

    pthread_mutex_init(&stack_mutex, NULL);  // Initialize the mutex

    // Create one thread for pushing and another for popping
    int start = 0;
    pthread_create(&thread1, NULL, push_thread_func, &start);
    pthread_create(&thread2, NULL, pop_thread_func, NULL);

    // Wait for both threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    // Cleanup
    pthread_mutex_destroy(&stack_mutex);

    return 0;
}
