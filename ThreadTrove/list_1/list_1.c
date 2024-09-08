#include <list_1.h>
#define N_THREADS 2  // Number of threads

// Thread function that performs operations on the list
void* thread_func(void* arg) {
    LinkedList* list = (LinkedList*)arg;  // Cast the argument to LinkedList pointer
    int thread_id = pthread_self();  // Get the thread's ID
    
    // Each thread inserts a value based on its thread ID (modulo 100 for uniqueness)
    int value_to_insert = thread_id % 100;
    insert(list, value_to_insert);
    printf("Thread %d inserted: %d into the list\n", thread_id, value_to_insert);
    
    // Each thread searches for the value it inserted
    Node* found_node = search(list, value_to_insert);
    if (found_node != NULL) {
        printf("Thread %d found value: %d\n", thread_id, found_node->data);
        
        // If found, increment the value
        found_node->data += 1;
        printf("Thread %d incremented value to: %d\n", thread_id, found_node->data);
    }
    
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
    free_list(&list);
    pthread_mutex_destroy(&list.lock);
    
    return 0;
}
