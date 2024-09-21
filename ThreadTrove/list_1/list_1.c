#include <list_1.h>
#define N_THREADS 2  // Number of threads

// Thread function that performs operations on the list
void* thread_func(void* arg) {
    LinkedList* list = (LinkedList*)arg;  // Cast the argument to LinkedList pointer
    int thread_id = pthread_self();  // Get the thread's ID
    int value;

    // Each thread inserts 100 random values 
    for(int i = 0; i < 50; i++){
        value = rand();
        insert(list, value);
        printf("Thread %d inserted: %d into the list\n", thread_id, value);
    }


    if (contains(list, value)!=false) {
        // If found, increment the value and insert after the current value
        insert_after(list, value, value+1); 
        printf("Thread %d incremented value to: %d\n", thread_id, value+1);
    }

    reverse(list);
    
    return NULL;
}

int main() {
    LinkedList list;
    init_list(&list);  // Initialize the linked list

    pthread_t threads[N_THREADS];  // Array of thread identifiers
    
    // Create N_THREADS threads, each executing thread_func
    for (int i = 0; i < N_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_func, &list);
    }

    // Join each thread (wait for them to finish)
    for (int i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // Display the final state of the list after all threads have executed
    display(&list);

    // Clean up the list and destroy the mutex lock
    clear(&list);
    pthread_mutex_destroy(&list.lock);
    
    return 0;
}
