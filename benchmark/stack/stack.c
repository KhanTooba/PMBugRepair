#include <stacks.h>
int main() {
    pthread_t thread1, thread2;

    pthread_mutex_init(&stack_mutex, NULL);  
	int start1 = 0;
    int start2 = 25;
    pthread_create(&thread1, NULL, thread_func, &start1);
    pthread_create(&thread2, NULL, thread_func, &start2);

    // Wait for both threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    // Cleanup
    pthread_mutex_destroy(&stack_mutex);

    return 0;
}
