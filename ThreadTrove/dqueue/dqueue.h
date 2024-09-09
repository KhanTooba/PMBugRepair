/*
 * This implementation provides a thread-safe Deque (Double-ended Queue) data structure using a doubly linked list.
 * It allows elements to be added or removed from both the front and rear of the deque, with thread safety ensured 
 * through the use of mutex locks. This implementation supports multiple threads, with write-after-write dependencies 
 * introduced in the thread function and the main method. The internal deque functions are unaware of these dependencies.
 * This code is part of a collection of lock-based data structures written in C.

 * Functions:
 * 
 * 1. Node* newNode(int data): Creates and returns a new node with the given data. Used internally by other functions.
 * 
 * 2. void deque_init(Deque* deque): Initializes the deque, setting the front and rear pointers to NULL and initializing 
 *    the mutex lock.
 * 
 * 3. void deque_push_front(Deque* deque, int data): Inserts an element at the front of the deque. If the deque is empty, 
 *    the new element becomes both the front and rear. Otherwise, the new element is added before the current front.
 * 
 * 4. void deque_push_back(Deque* deque, int data): Inserts an element at the rear of the deque. If the deque is empty, 
 *    the new element becomes both the front and rear. Otherwise, the new element is added after the current rear.
 * 
 * 5. int deque_pop_front(Deque* deque): Removes and returns an element from the front of the deque. If the deque is empty, 
 *    it returns -1. The front pointer is updated, and if the deque becomes empty, the rear pointer is also set to NULL.
 * 
 * 6. int deque_pop_back(Deque* deque): Removes and returns an element from the rear of the deque. If the deque is empty, 
 *    it returns -1. The rear pointer is updated, and if the deque becomes empty, the front pointer is also set to NULL.
 * 
 * 7. int deque_is_empty(Deque* deque): Checks if the deque is empty. Returns 1 if empty, 0 otherwise.
 * 
 * 8. void deque_clear(Deque* deque): Clears all elements from the deque. Frees all nodes and sets the front and rear 
 *    pointers to NULL.
 * 
 * 9. void deque_destroy(Deque* deque): Clears the deque and destroys the mutex lock associated with it.
 * 
 * 10. void deque_print(Deque* deque): Prints all elements currently in the deque from front to rear.
 * 
 * 11. void* thread_func(void* arg): A thread function that simulates write-after-write dependencies by performing 
 *     multiple operations on the deque. Each thread pops an element from the front, modifies it, and pushes it back, 
 *     introducing dependencies between operations.
 * 
 * 12. int main(): Initializes the deque, inserts some initial values, creates multiple threads to perform operations, 
 *     waits for all threads to complete, prints the final state of the deque, and destroys the deque.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

// Node structure for the deque
typedef struct Node {
    int data;
    struct Node* next;
    struct Node* prev;
} Node;

// Deque structure
typedef struct Deque {
    Node* front;
    Node* rear;
    pthread_mutex_t lock;
} Deque;

// Function to create a new node
Node* newNode(int data) {
    Node* node = (Node*)pmalloc(sizeof(Node));
    node->data = data;
    node->next = NULL;
    node->prev = NULL;
    return node;
}

// Initialize the deque
void deque_init(Deque* deque) {
    deque->front = deque->rear = NULL;
    pthread_mutex_init(&deque->lock, NULL);
}

// Insert an element at the front of the deque
void deque_push_front(Deque* deque, int data) {
    pthread_mutex_lock(&deque->lock);

    Node* node = newNode(data);
    if (deque->front == NULL) {
        deque->front = deque->rear = node;
    } else {
        node->next = deque->front;
        deque->front->prev = node;
        deque->front = node;
    }

    pthread_mutex_unlock(&deque->lock);
}

// Insert an element at the rear of the deque
void deque_push_back(Deque* deque, int data) {
    pthread_mutex_lock(&deque->lock);

    Node* node = newNode(data);
    if (deque->rear == NULL) {
        deque->front = deque->rear = node;
    } else {
        node->prev = deque->rear;
        deque->rear->next = node;
        deque->rear = node;
    }

    pthread_mutex_unlock(&deque->lock);
}

// Remove an element from the front of the deque
int deque_pop_front(Deque* deque) {
    pthread_mutex_lock(&deque->lock);

    if (deque->front == NULL) {
        pthread_mutex_unlock(&deque->lock);
        return -1; // Deque is empty
    }

    int data = deque->front->data;
    Node* temp = deque->front;
    deque->front = deque->front->next;

    if (deque->front == NULL) {
        deque->rear = NULL;
    } else {
        deque->front->prev = NULL;
    }

    free(temp);
    pthread_mutex_unlock(&deque->lock);
    return data;
}

// Remove an element from the rear of the deque
int deque_pop_back(Deque* deque) {
    pthread_mutex_lock(&deque->lock);

    if (deque->rear == NULL) {
        pthread_mutex_unlock(&deque->lock);
        return -1; // Deque is empty
    }

    int data = deque->rear->data;
    Node* temp = deque->rear;
    deque->rear = deque->rear->prev;

    if (deque->rear == NULL) {
        deque->front = NULL;
    } else {
        deque->rear->next = NULL;
    }

    free(temp);
    pthread_mutex_unlock(&deque->lock);
    return data;
}

// Check if the deque is empty
int deque_is_empty(Deque* deque) {
    pthread_mutex_lock(&deque->lock);
    int is_empty = (deque->front == NULL);
    pthread_mutex_unlock(&deque->lock);
    return is_empty;
}

// Clear the deque
void deque_clear(Deque* deque) {
    pthread_mutex_lock(&deque->lock);

    Node* current = deque->front;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }

    deque->front = deque->rear = NULL;

    pthread_mutex_unlock(&deque->lock);
}

// Destroy the deque
void deque_destroy(Deque* deque) {
    deque_clear(deque);
    pthread_mutex_destroy(&deque->lock);
}

// Print the elements of the deque
void deque_print(Deque* deque) {
    pthread_mutex_lock(&deque->lock);

    Node* current = deque->front;
    printf("Deque: ");
    while (current != NULL) {
        printf("%d ", current->data);
        current = current->next;
    }
    printf("\n");

    pthread_mutex_unlock(&deque->lock);
}

