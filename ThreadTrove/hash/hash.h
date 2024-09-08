/*
 * Hash Table Data Structure in C with Multithreading
 *
 * This implementation of the hash table data structure is part of **ThreadTrove**, 
 * a collection of lock-based concurrent data structures written in C. The hash table 
 * is designed to be thread-safe, allowing multiple threads to perform operations 
 * concurrently while preventing data corruption. Synchronization is achieved using 
 * mutex locks to control access to shared data, ensuring safe concurrent inserts, 
 * deletions, lookups, and updates.
 *
 * In this implementation, threads can introduce write-after-read dependencies 
 * through the `thread_func` function and the `main` method. However, the internal 
 * hash table functions are unaware of these dependencies, ensuring that the data 
 * structure's core logic remains independent and reliable.
 *
 * Functions:
 * 
 * - `void init_hash_table(HashTable* table)`:
 *     Initializes the hash table with a fixed number of buckets and sets each 
 *     bucket to NULL. Also initializes the mutex lock to enable thread-safe access.
 *
 * - `void insert(HashTable* table, int key, int value)`:
 *     Inserts a key-value pair into the hash table. Handles collisions using 
 *     separate chaining (linked lists). This function is protected by a mutex lock 
 *     to ensure thread safety.
 *
 * - `bool delete_from_hash(HashTable* table, int key)`:
 *     Deletes the key-value pair associated with the specified key. If the key 
 *     is found, it is removed from the hash table. Returns true if the deletion 
 *     is successful, false if the key is not found. This function is protected by a mutex lock.
 *
 * - `int get(HashTable* table, int key)`:
 *     Retrieves the value associated with the specified key. If the key is not 
 *     found, it returns `-1`. The function ensures thread-safe access using a mutex lock.
 *
 * - `void update(HashTable* table, int key, int value)`:
 *     Updates the value associated with the specified key. If the key is not 
 *     found, the function does nothing. It uses a mutex lock to ensure thread-safe access.
 *
 * - `bool contains(HashTable* table, int key)`:
 *     Checks if the specified key exists in the hash table. Returns true if 
 *     the key is found, false otherwise. The function is protected by a mutex lock.
 *
 * - `void clear(HashTable* table)`:
 *     Clears the hash table by removing all key-value pairs and freeing associated memory. 
 *     This function is thread-safe due to the use of a mutex lock.
 *
 * - `int size(HashTable* table)`:
 *     Returns the number of key-value pairs currently in the hash table. 
 *     Ensures thread safety using a mutex lock.
 *
 * - `bool is_empty(HashTable* table)`:
 *     Checks if the hash table is empty by comparing its size to zero. 
 *     Thread-safe due to a mutex lock.
 *
 * - `int hash_function(int key)`:
 *     Hashes the given key and returns the index of the corresponding bucket. 
 *     This function is used internally by the hash table and is not thread-sensitive.
 *
 * - `void display(HashTable* table)`:
 *     Prints the contents of the hash table to the console, showing each 
 *     key-value pair in its bucket. The function locks the hash table to ensure 
 *     correct data display in a multithreaded environment.
 *
 * - `void merge(HashTable* table, HashTable* other)`:
 *     Merges another hash table into the current hash table by inserting each 
 *     key-value pair from the other hash table. Ensures thread safety with a mutex lock.
 *
 * This hash table implementation is part of the **ThreadTrove** collection, which provides 
 * a variety of lock-based concurrent data structures in C, designed to handle 
 * multithreading scenarios efficiently.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>
#include <stdbool.h>
#include "pm.h"

#define TABLE_SIZE 10  // Size of the hash table

typedef struct Node {
    int key;
    int value;
    struct Node* next;
} Node;

typedef struct HashTable {
    Node* buckets[TABLE_SIZE];
    int size;
    pthread_mutex_t lock;
} HashTable;

// Hash function
int hash_function(int key) {
    return key % TABLE_SIZE;
}

// Initialize hash table
void init_hash_table(HashTable* table) {
    table->size = 0;
    pthread_mutex_init(&table->lock, NULL);
    for (int i = 0; i < TABLE_SIZE; i++) {
        table->buckets[i] = NULL;
    }
}

// Insert key-value pair into hash table
void insert(HashTable* table, int key, int value) {
    int index = hash_function(key);
    
    pthread_mutex_lock(&table->lock);
    
    Node* new_node = (Node*)pmalloc(sizeof(Node));
    new_node->key = key;
    new_node->value = value;
    new_node->next = table->buckets[index];
    table->buckets[index] = new_node;
    table->size++;
    
    pthread_mutex_unlock(&table->lock);
}

// Delete key-value pair from hash table
bool delete_from_hash(HashTable* table, int key) {
    int index = hash_function(key);
    
    pthread_mutex_lock(&table->lock);
    
    Node* current = table->buckets[index];
    Node* prev = NULL;
    
    while (current != NULL && current->key != key) {
        prev = current;
        current = current->next;
    }
    
    if (current == NULL) {
        pthread_mutex_unlock(&table->lock);
        return false;  // Key not found
    }
    
    if (prev == NULL) {
        table->buckets[index] = current->next;
    } else {
        prev->next = current->next;
    }
    
    free(current);
    table->size--;
    
    pthread_mutex_unlock(&table->lock);
    return true;
}

// Get value associated with a key
int get(HashTable* table, int key) {
    int index = hash_function(key);
    
    pthread_mutex_lock(&table->lock);
    
    Node* current = table->buckets[index];
    
    while (current != NULL) {
        if (current->key == key) {
            int value = current->value;
            pthread_mutex_unlock(&table->lock);
            return value;
        }
        current = current->next;
    }
    
    pthread_mutex_unlock(&table->lock);
    return -1;  // Key not found
}

// Update value associated with a key
void update(HashTable* table, int key, int value) {
    int index = hash_function(key);
    
    pthread_mutex_lock(&table->lock);
    
    Node* current = table->buckets[index];
    
    while (current != NULL) {
        if (current->key == key) {
            current->value = value;
            pthread_mutex_unlock(&table->lock);
            return;
        }
        current = current->next;
    }
    
    pthread_mutex_unlock(&table->lock);
}

// Check if key exists in hash table
bool contains(HashTable* table, int key) {
    return get(table, key) != -1;
}

// Clear hash table
void clear(HashTable* table) {
    pthread_mutex_lock(&table->lock);
    
    for (int i = 0; i < TABLE_SIZE; i++) {
        Node* current = table->buckets[i];
        while (current != NULL) {
            Node* to_free = current;
            current = current->next;
            free(to_free);
        }
        table->buckets[i] = NULL;
    }
    
    table->size = 0;
    
    pthread_mutex_unlock(&table->lock);
}

// Get the current size of the hash table
int size(HashTable* table) {
    pthread_mutex_lock(&table->lock);
    int current_size = table->size;
    pthread_mutex_unlock(&table->lock);
    return current_size;
}

// Check if the hash table is empty
bool is_empty(HashTable* table) {
    return size(table) == 0;
}

// Display the contents of the hash table
void display(HashTable* table) {
    pthread_mutex_lock(&table->lock);
    
    for (int i = 0; i < TABLE_SIZE; i++) {
        Node* current = table->buckets[i];
        printf("Bucket %d: ", i);
        while (current != NULL) {
            printf("(%d, %d) -> ", current->key, current->value);
            current = current->next;
        }
        printf("NULL\n");
    }
    
    pthread_mutex_unlock(&table->lock);
}

// Merge another hash table into the current hash table
void merge(HashTable* table, HashTable* other) {
    pthread_mutex_lock(&table->lock);
    pthread_mutex_lock(&other->lock);
    for (int i = 0; i < TABLE_SIZE; i++) {
        Node* current = other->buckets[i];
        while (current != NULL) {
            insert(table, current->key, current->value);
            current = current->next;
        }
    }
    pthread_mutex_lock(&other->lock);
    pthread_mutex_lock(&table->lock);
}