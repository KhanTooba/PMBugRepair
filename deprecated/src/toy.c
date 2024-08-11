#include <stdio.h>
#include <pthread.h>

// Overridden operator new function
void *operator new(size_t size) {
    void *ret;
    posix_memalign(&ret, 64, size);
    return ret;
}

int *x;
int *y;

void *thread1_function(void *arg) {
    // Store value 10 in variable x
    *x = 10;

    pthread_exit(NULL);
}

void *thread2_function(void *arg) {
    // Read value of x from persistent memory and store it in y
    *y = *x;

    pthread_exit(NULL);
}

int main() {
    pthread_t thread1, thread2;

    // Allocate memory for x and y
    x = new int;
    y = new int;

    // Create thread 1
    if (pthread_create(&thread1, NULL, thread1_function, NULL) != 0) {
        perror("Error creating thread 1");
        return 1;
    }

    // Create thread 2
    if (pthread_create(&thread2, NULL, thread2_function, NULL) != 0) {
        perror("Error creating thread 2");
        return 1;
    }

    // Wait for both threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    return 0;
}
