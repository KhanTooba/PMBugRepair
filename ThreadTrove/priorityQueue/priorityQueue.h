/*
 * This implementation provides a thread-safe priority queue data structure using a linked list.
 * It is designed to handle concurrent operations with multiple threads, making use of locks to
 * ensure safe access to the data structure. 

 * This is a part of a collection of lock-based data structures written in C.

 * Functions:
 * 1. newNode(int data, int priority):
 *    - Creates a new node with the given data and priority.
 *    - Returns a pointer to the newly created node.
 * 
 * 2. pq_init(PriorityQueue* pq):
 *    - Initializes the priority queue by setting the head to NULL and initializing the mutex lock.
 * 
 * 3. pq_insert(PriorityQueue* pq, int data, int priority):
 *    - Inserts a new node into the priority queue based on the priority value.
 *    - If the queue is empty or the new node has the highest priority, it becomes the new head.
 *    - Otherwise, the node is inserted at the appropriate position in the list.
 *    - Thread-safe with a mutex lock for concurrent access.
 * 
 * 4. pq_extract_min(PriorityQueue* pq):
 *    - Removes and returns the element with the highest priority (lowest value).
 *    - If the queue is empty, it returns -1 and prints a message.
 *    - Thread-safe with a mutex lock for concurrent access.
 * 
 * 5. pq_peek(PriorityQueue* pq):
 *    - Returns the element with the highest priority without removing it from the queue.
 *    - If the queue is empty, it returns -1 and prints a message.
 *    - Thread-safe with a mutex lock for concurrent access.
 * 
 * 6. pq_is_empty(PriorityQueue* pq):
 *    - Checks if the priority queue is empty.
 *    - Returns 1 if the queue is empty, 0 otherwise.
 *    - Thread-safe with a mutex lock for concurrent access.
 * 
 * 7. pq_size(PriorityQueue* pq):
 *    - Returns the number of elements in the priority queue.
 *    - Traverses the linked list to count the nodes.
 *    - Thread-safe with a mutex lock for concurrent access.
 * 
 * 8. pq_clear(PriorityQueue* pq):
 *    - Clears the priority queue by freeing all nodes.
 *    - Sets the head to NULL after clearing the list.
 *    - Thread-safe with a mutex lock for concurrent access.
 * 
 * 9. pq_destroy(PriorityQueue* pq):
 *    - Destroys the priority queue by clearing it and destroying the mutex lock.
 * 
 * 10. thread_func(void* arg):
 *    - A thread function that extracts the minimum element, modifies it, and reinserts it
 *      with a higher priority, simulating a write-after-write dependency.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

// Node structure for the priority queue
typedef struct Node {
    int data;
    int priority;
    struct Node* next;
} Node;

// Priority Queue structure
typedef struct PriorityQueue {
    Node* head;
    pthread_mutex_t lock;  // Lock for thread synchronization
} PriorityQueue;

// Function to create a new node
Node* newNode(int data, int priority) {
    Node* temp = (Node*)pmalloc(sizeof(Node));
    temp->data = data;
    temp->priority = priority;
    temp->next = NULL;
    return temp;
}

// Initialize the priority queue
void pq_init(PriorityQueue* pq) {
    pq->head = NULL;
    pthread_mutex_init(&(pq->lock), NULL);
}

// Insert an element into the priority queue based on priority
void pq_insert(PriorityQueue* pq, int data, int priority) {
    pthread_mutex_lock(&(pq->lock));  // Lock for safe concurrent access

    Node* temp = newNode(data, priority);

    // Special case: the head is NULL or the new node has a higher priority than the head
    if (pq->head == NULL || pq->head->priority > priority) {
        temp->next = pq->head;
        pq->head = temp;
    } else {
        // Traverse the list and find the correct position to insert
        Node* start = pq->head;
        while (start->next != NULL && start->next->priority <= priority) {
            start = start->next;
        }
        temp->next = start->next;
        start->next = temp;
    }

    printf("Inserted %d with priority %d into the priority queue\n", data, priority);

    pthread_mutex_unlock(&(pq->lock));  // Unlock after the operation
}

// Remove and return the element with the highest priority (lowest value)
int pq_extract_min(PriorityQueue* pq) {
    pthread_mutex_lock(&(pq->lock));  // Lock for safe concurrent access

    if (pq->head == NULL) {
        printf("Priority queue underflow\n");
        pthread_mutex_unlock(&(pq->lock));  // Unlock before returning
        return -1;
    }

    Node* temp = pq->head;
    int min = temp->data;
    pq->head = pq->head->next;
    free(temp);

    printf("Extracted %d from the priority queue\n", min);

    pthread_mutex_unlock(&(pq->lock));  // Unlock after the operation
    return min;
}

// Peek at the element with the highest priority without removing it
int pq_peek(PriorityQueue* pq) {
    pthread_mutex_lock(&(pq->lock));  // Lock for safe concurrent access

    if (pq->head == NULL) {
        printf("Priority queue is empty\n");
        pthread_mutex_unlock(&(pq->lock));  // Unlock before returning
        return -1;
    }

    int min = pq->head->data;

    pthread_mutex_unlock(&(pq->lock));  // Unlock after the operation
    return min;
}

// Check if the priority queue is empty
int pq_is_empty(PriorityQueue* pq) {
    pthread_mutex_lock(&(pq->lock));  // Lock for safe concurrent access
    int empty = (pq->head == NULL);
    pthread_mutex_unlock(&(pq->lock));  // Unlock after the operation
    return empty;
}

// Get the size of the priority queue
int pq_size(PriorityQueue* pq) {
    pthread_mutex_lock(&(pq->lock));  // Lock for safe concurrent access
    int size = 0;
    Node* temp = pq->head;
    while (temp != NULL) {
        size++;
        temp = temp->next;
    }
    pthread_mutex_unlock(&(pq->lock));  // Unlock after the operation
    return size;
}

// Clear the priority queue
void pq_clear(PriorityQueue* pq) {
    pthread_mutex_lock(&(pq->lock));  // Lock for safe concurrent access

    Node* temp = pq->head;
    while (temp != NULL) {
        Node* next = temp->next;
        free(temp);
        temp = next;
    }
    pq->head = NULL;

    pthread_mutex_unlock(&(pq->lock));  // Unlock after the operation
}

// Free the priority queue (destroy the mutex lock)
void pq_destroy(PriorityQueue* pq) {
    pq_clear(pq);
    pthread_mutex_destroy(&(pq->lock));
}