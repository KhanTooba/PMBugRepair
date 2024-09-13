/*
 * Queue Data Structure (Lock-Based Implementation)
 *
 * This queue is part of a collection of lock-based data structures written in C.
 * It implements a thread-safe, dynamic queue using a linked list, allowing multiple
 * threads to concurrently perform enqueue, dequeue, and other operations. 
 * The queue uses a first-in-first-out (FIFO) order for handling elements.
 *
 * To ensure thread safety during concurrent operations, mutex locks are employed 
 * to synchronize access to the queue. The queue's internal functions remain unaware
 * of the multithreading details, providing a clean separation between thread management
 * and data structure functionality.
 *
 * Functions:
 *
 * 1. Node* createNode(int data):
 *    - Creates and initializes a new node with the given data.
 *    - This node will be used in the linked list representation of the queue.
 *
 * 2. Queue* createQueue():
 *    - Initializes a new queue, setting the front and rear pointers to NULL.
 *    - Initializes a mutex lock for the queue to ensure thread-safe operations.
 *
 * 3. int isEmpty(Queue* queue):
 *    - Checks whether the queue is empty by verifying if the front pointer is NULL.
 *    - Returns 1 if the queue is empty, otherwise returns 0.
 *
 * 4. void enqueue(Queue* queue, int data):
 *    - Inserts a new element at the rear of the queue.
 *    - The function locks the queue to ensure that only one thread can modify
 *      the queue at a time. After insertion, the lock is released.
 *    - Handles the base case where the queue is initially empty.
 *
 * 5. int dequeue(Queue* queue):
 *    - Removes and returns the front element of the queue.
 *    - If the queue is empty, it prints a message and returns -1.
 *    - Uses locking to ensure that only one thread can remove an element at a time.
 *    - Handles the base case where the queue becomes empty after the operation.
 *
 * 6. int front(Queue* queue):
 *    - Returns the front element of the queue without removing it.
 *    - If the queue is empty, it prints a message and returns -1.
 *    - Locks the queue during access to ensure thread-safe operations.
 *
 * 7. void printQueue(Queue* queue):
 *    - Prints all the elements of the queue in order, starting from the front to the rear.
 *    - Uses locking to ensure that the queue can be safely accessed by multiple threads.
 *    - Prints a message if the queue is empty.
 *
 * This queue is designed to provide a simple yet efficient solution for managing concurrent
 * operations in a multithreaded environment. With proper locking mechanisms and separation of
 * dependency management, this data structure ensures safety and flexibility in its operations.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

// Node structure for the linked list
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Queue structure
typedef struct Queue {
    Node* front;
    Node* rear;
    pthread_mutex_t lock;  // Lock for concurrent operations
} Queue;

// Function to create a new node
Node* createNode(int data) {
    Node* newNode = (Node*)pmalloc(sizeof(Node));
    newNode->data = data;
    newNode->next = NULL;
    return newNode;
}

// Function to initialize a queue
Queue* createQueue() {
    Queue* queue = (Queue*)pmalloc(sizeof(Queue));
    queue->front = queue->rear = NULL;
    pthread_mutex_init(&queue->lock, NULL);  // Initialize the lock
    return queue;
}

// Function to check if the queue is empty
int isEmpty(Queue* queue) {
    return queue->front == NULL;
}

// Function to enqueue an element to the queue
void enqueue(Queue* queue, int data) {
    Node* newNode = createNode(data);

    // Lock the queue for thread-safe operation
    pthread_mutex_lock(&queue->lock);

    if (queue->rear == NULL) {
        queue->front = queue->rear = newNode;
    } else {
        queue->rear->next = newNode;
        queue->rear = newNode;
    }

    // Unlock the queue
    pthread_mutex_unlock(&queue->lock);
}

// Function to dequeue an element from the queue
int dequeue(Queue* queue) {
    if (isEmpty(queue)) {
        printf("Queue underflow\n");
        return -1;
    }

    // Lock the queue for thread-safe operation
    pthread_mutex_lock(&queue->lock);

    Node* temp = queue->front;
    int data = temp->data;
    queue->front = queue->front->next;

    if (queue->front == NULL) {
        queue->rear = NULL;
    }

    free(temp);

    // Unlock the queue
    pthread_mutex_unlock(&queue->lock);

    return data;
}

// Function to get the front element of the queue
int front(Queue* queue) {
    if (isEmpty(queue)) {
        printf("Queue is empty\n");
        return -1;
    }

    // Lock the queue for thread-safe operation
    pthread_mutex_lock(&queue->lock);
    int data = queue->front->data;
    pthread_mutex_unlock(&queue->lock);

    return data;
}

// Function to print the queue elements
void printQueue(Queue* queue) {
    if (isEmpty(queue)) {
        printf("Queue is empty\n");
        return;
    }

    // Lock the queue for thread-safe operation
    pthread_mutex_lock(&queue->lock);

    Node* temp = queue->front;
    printf("Queue: ");
    while (temp != NULL) {
        printf("%d ", temp->data);
        temp = temp->next;
    }
    printf("\n");

    // Unlock the queue
    pthread_mutex_unlock(&queue->lock);
}