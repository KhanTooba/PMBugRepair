#include<array.h>
#define N_THREADS 2          // Default number of threads

// Thread function that performs operations on the array
void* thread_func(void* arg) {
    Array* arr = (Array*)arg;
    int thread_id = pthread_self();

    // Insert elements based on thread ID
    insert(arr, thread_id % 100);
    printf("Thread %d inserted: %d into the array\n", thread_id, thread_id % 100);

    int value_read = get(arr, size(arr)-1);
    if (value_read != -1) {
        printf("Thread %d read: %d from the array\n", thread_id, value_read);
        // delete_element(arr, 0);  // Delete the element after reading
        insert(arr, value_read+1);
        printf("Thread %d inserted: %d into the array\n", thread_id, value_read+1);
        // printf("Thread %d deleted: %d from the array\n", thread_id, value_read);
    }

    return NULL;
}

int main() {
    Array arr;
    init_array(&arr);  // Initialize the array

    int n_threads = N_THREADS;  // Set the number of threads

    pthread_t threads[n_threads];  // Array of thread identifiers

    // Create n_threads, each executing the thread_func
    for (int i = 0; i < n_threads; i++) {
        if (pthread_create(&threads[i], NULL, thread_func, &arr) != 0) {
            perror("Failed to create thread");
            return 1;
        }
    }

    // Join all threads
    for (int i = 0; i < n_threads; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            perror("Failed to join thread");
            return 1;
        }
    }

    // Display the final contents of the array
    printf("Final contents of the array:\n");
    display(&arr);

    // Clean up
    pthread_mutex_destroy(&arr.lock);  // Destroy the mutex lock
    free(arr.data);  // Free the allocated memory

    return 0;
}
