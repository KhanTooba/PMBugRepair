#include<hash.h>
#define N_THREADS 2    // Default number of threads

// Thread function that performs operations on the hash table
void* thread_func(void* arg) {
    HashTable* ht = (HashTable*)arg;
    int thread_id = pthread_self();
    int key_to_insert;
    int value_to_insert;

    // Each thread inserts 100 random values 
    for(int i = 0; i < 30; i++){
        key_to_insert = rand();
        value_to_insert = rand()%100;
        insert(ht, key_to_insert, value_to_insert);
        printf("Thread %d inserted: (%d, %d) into the hash table\n", thread_id, key_to_insert, value_to_insert);
    }

    if (contains(ht, key_to_insert) != false) {
        printf("Thread %d read: (%d, %d) from the hash table\n", thread_id, key_to_insert, get(ht, key_to_insert));
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
