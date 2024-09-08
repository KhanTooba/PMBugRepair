#include<hash.h>
#define N_THREADS 2    // Default number of threads

// Thread function that performs operations on the hash table
void* thread_func(void* arg) {
    HashTable* ht = (HashTable*)arg;
    int thread_id = pthread_self();
    
    // Each thread inserts a key-value pair based on its ID
    int key_to_insert = thread_id % 100;
    int value_to_insert = key_to_insert * 2;
    insert(ht, key_to_insert, value_to_insert);
    printf("Thread %d inserted: (%d, %d) into the hash table\n", thread_id, key_to_insert, value_to_insert);
    
    int value_read = search(ht, key_to_insert);
    if (value_read != -1) {
        printf("Thread %d read: (%d, %d) from the hash table\n", thread_id, key_to_insert, value_read);
        delete_from_hash(ht, key_to_insert);  // Delete the key after reading
        printf("Thread %d deleted: (%d) from the hash table\n", thread_id, key_to_insert);
    }
    
    return NULL;
}

int main() {
    HashTable ht;
    init_hash_table(&ht);  // Initialize the hash table

    pthread_t threads[N_THREADS];  // Array of thread identifiers
    
    // Create N_THREADS threads, each executing thread_func
    for (int i = 0; i < N_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_func, &ht);
    }

    // Join each thread (wait for them to finish)
    for (int i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // Display the final state of the hash table after all threads have executed
    display(&ht);

    // Clean up the hash table and destroy the mutex locks
    clear(&ht);
    
    return 0;
}
