/*
 * This implementation provides a thread-safe set data structure using a linked list.
 * It allows concurrent insertions, deletions, and lookups, ensuring correctness through the use of mutex locks.
 * The set supports multiple threads, with a write-after-write dependency introduced in the thread function and main method.
 * The internal functions of the set are unaware of this dependency, ensuring modularity and simplicity.
 * This implementation is part of a collection of lock-based data structures written in C.

 * Functions:
 * 1. newNode(int data): Creates a new node with the given data. Used internally by the set functions.
 *
 * 2. set_init(Set* set): Initializes the set, setting the head pointer to NULL and initializing the mutex lock.
 *
 * 3. set_insert(Set* set, int data): Inserts a new element into the set if it doesn't already exist. 
 *    The insertion happens at the beginning of the linked list for efficiency.
 *
 * 4. set_remove(Set* set, int data): Removes an element from the set if it exists. The element is found by traversing 
 *    the linked list, and if found, it is removed from the list.
 *
 * 5. set_contains(Set* set, int data): Checks if a given element exists in the set. This function traverses the linked list 
 *    and returns 1 if the element is found, otherwise it returns 0.
 *
 * 6. set_clear(Set* set): Clears all elements from the set. This function traverses the linked list, freeing each node 
 *    and setting the head pointer to NULL.
 *
 * 7. set_destroy(Set* set): Clears the set by removing all elements and destroys the mutex lock associated with the set.
 *
 * 8. set_print(Set* set): Prints all elements currently in the set by traversing the linked list.
 *
 * 9. thread_func(void* arg): A thread function that simulates a write-after-write dependency. Each thread removes an element 
 *    from the set, modifies it, and reinserts it. The internal set functions are unaware of this dependency.
 *
 * 10. main(): The entry point of the program. It initializes the set, inserts some initial values, creates multiple threads, 
 *     and waits for them to complete. Finally, it prints the final state of the set and destroys the set to free resources.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

// Node structure for the set
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Set structure with head pointer and a mutex lock for thread safety
typedef struct {
    Node* head;
    pthread_mutex_t lock;
} Set;

// Function to create a new node
Node* newNode(int data) {
    Node* node = (Node*)pmalloc(sizeof(Node));
    node->data = data;
    node->next = NULL;
    return node;
}

// Initialize the set
void set_init(Set* set) {
    set->head = NULL;
    pthread_mutex_init(&set->lock, NULL);
}

// Insert an element into the set (no duplicates)
void set_insert(Set* set, int data) {
    pthread_mutex_lock(&set->lock);

    // Check if the element already exists
    Node* curr = set->head;
    while (curr != NULL) {
        if (curr->data == data) {
            pthread_mutex_unlock(&set->lock);
            return; // Element already exists
        }
        curr = curr->next;
    }

    // Insert new element at the beginning
    Node* new_node = newNode(data);
    new_node->next = set->head;
    set->head = new_node;

    pthread_mutex_unlock(&set->lock);
}

// Remove an element from the set
void set_remove(Set* set, int data) {
    pthread_mutex_lock(&set->lock);

    Node* curr = set->head;
    Node* prev = NULL;

    while (curr != NULL && curr->data != data) {
        prev = curr;
        curr = curr->next;
    }

    // Element not found
    if (curr == NULL) {
        pthread_mutex_unlock(&set->lock);
        return;
    }

    // Remove the element
    if (prev == NULL) {
        set->head = curr->next;
    } else {
        prev->next = curr->next;
    }
    free(curr);

    pthread_mutex_unlock(&set->lock);
}

// Check if an element exists in the set
int set_contains(Set* set, int data) {
    pthread_mutex_lock(&set->lock);

    Node* curr = set->head;
    while (curr != NULL) {
        if (curr->data == data) {
            pthread_mutex_unlock(&set->lock);
            return 1; // Element found
        }
        curr = curr->next;
    }

    pthread_mutex_unlock(&set->lock);
    return 0; // Element not found
}

// Clear all elements from the set
void set_clear(Set* set) {
    pthread_mutex_lock(&set->lock);

    Node* curr = set->head;
    while (curr != NULL) {
        Node* temp = curr;
        curr = curr->next;
        free(temp);
    }
    set->head = NULL;

    pthread_mutex_unlock(&set->lock);
}

// Destroy the set and free the resources
void set_destroy(Set* set) {
    set_clear(set);
    pthread_mutex_destroy(&set->lock);
}

// Function to print all elements in the set
void set_print(Set* set) {
    pthread_mutex_lock(&set->lock);

    Node* curr = set->head;
    printf("Set elements: ");
    while (curr != NULL) {
        printf("%d ", curr->data);
        curr = curr->next;
    }
    printf("\n");

    pthread_mutex_unlock(&set->lock);
}