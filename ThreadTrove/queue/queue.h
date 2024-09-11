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