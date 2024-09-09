/*
 * This implementation provides a thread-safe Doubly Linked List data structure using a doubly linked list with mutex locks
 * to handle concurrent operations. It supports multiple threads, with write-after-write dependencies introduced in the thread
 * function and the main method. The internal functions of the doubly linked list are not aware of these dependencies. 
 * This code is part of a collection of lock-based data structures written in C.
 * 
 * Functions:
 * 
 * 1. Node* newNode(int data): Creates and returns a new node with the given data. The node's next and prev pointers are initialized to NULL.
 * 
 * 2. void dll_init(DoublyLinkedList* list): Initializes the doubly linked list, setting the head and tail pointers to NULL and initializing
 *    the mutex lock to ensure thread safety.
 * 
 * 3. void dll_insert_end(DoublyLinkedList* list, int data): Inserts an element with the given data at the end of the list. If the list is empty,
 *    the new element becomes both the head and tail. Otherwise, the new element is added after the current tail.
 * 
 * 4. void dll_insert_start(DoublyLinkedList* list, int data): Inserts an element with the given data at the beginning of the list. If the list is empty,
 *    the new element becomes both the head and tail. Otherwise, the new element is added before the current head.
 * 
 * 5. int dll_remove_end(DoublyLinkedList* list): Removes and returns an element from the end of the list. If the list is empty, it returns -1.
 *    The tail pointer is updated, and if the list becomes empty, the head pointer is also set to NULL.
 * 
 * 6. int dll_remove_start(DoublyLinkedList* list): Removes and returns an element from the beginning of the list. If the list is empty, it returns -1.
 *    The head pointer is updated, and if the list becomes empty, the tail pointer is also set to NULL.
 * 
 * 7. int dll_is_empty(DoublyLinkedList* list): Checks if the list is empty. Returns 1 if the list is empty, 0 otherwise.
 * 
 * 8. void dll_clear(DoublyLinkedList* list): Clears all elements from the list. Frees all nodes and sets the head and tail pointers to NULL.
 * 
 * 9. void dll_destroy(DoublyLinkedList* list): Clears the list and destroys the mutex lock associated with it.
 * 
 * 10. void dll_print(DoublyLinkedList* list): Prints all elements currently in the list from head to tail.
 * 
 * 11. void* thread_func(void* arg): A thread function that simulates write-after-write dependencies by performing multiple operations 
 *     on the list. Each thread removes an element from the start, modifies it, inserts it at the end, inserts another element at the start,
 *     and then removes an element from the end, introducing dependencies between operations.
 * 
 * 12. int main(): Initializes the list, inserts some initial values, creates multiple threads to perform operations, waits for all threads 
 *     to complete, prints the final state of the list, and destroys the list.
 */


#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"


// Node structure for the doubly linked list
typedef struct Node {
    int data;
    struct Node* next;
    struct Node* prev;
} Node;

// Doubly Linked List structure
typedef struct DoublyLinkedList {
    Node* head;
    Node* tail;
    pthread_mutex_t lock;
} DoublyLinkedList;

// Function to create a new node
Node* newNode(int data) {
    Node* node = (Node*)pmalloc(sizeof(Node));
    node->data = data;
    node->next = NULL;
    node->prev = NULL;
    return node;
}

// Initialize the doubly linked list
void dll_init(DoublyLinkedList* list) {
    list->head = list->tail = NULL;
    pthread_mutex_init(&list->lock, NULL);
}

// Insert an element at the end of the list
void dll_insert_end(DoublyLinkedList* list, int data) {
    pthread_mutex_lock(&list->lock);

    Node* node = newNode(data);
    if (list->tail == NULL) {
        list->head = list->tail = node;
    } else {
        list->tail->next = node;
        node->prev = list->tail;
        list->tail = node;
    }

    pthread_mutex_unlock(&list->lock);
}

// Insert an element at the beginning of the list
void dll_insert_start(DoublyLinkedList* list, int data) {
    pthread_mutex_lock(&list->lock);

    Node* node = newNode(data);
    if (list->head == NULL) {
        list->head = list->tail = node;
    } else {
        list->head->prev = node;
        node->next = list->head;
        list->head = node;
    }

    pthread_mutex_unlock(&list->lock);
}

// Remove an element from the end of the list
int dll_remove_end(DoublyLinkedList* list) {
    pthread_mutex_lock(&list->lock);

    if (list->tail == NULL) {
        pthread_mutex_unlock(&list->lock);
        return -1; // List is empty
    }

    int data = list->tail->data;
    Node* temp = list->tail;
    list->tail = list->tail->prev;

    if (list->tail == NULL) {
        list->head = NULL;
    } else {
        list->tail->next = NULL;
    }

    free(temp);
    pthread_mutex_unlock(&list->lock);
    return data;
}

// Remove an element from the beginning of the list
int dll_remove_start(DoublyLinkedList* list) {
    pthread_mutex_lock(&list->lock);

    if (list->head == NULL) {
        pthread_mutex_unlock(&list->lock);
        return -1; // List is empty
    }

    int data = list->head->data;
    Node* temp = list->head;
    list->head = list->head->next;

    if (list->head == NULL) {
        list->tail = NULL;
    } else {
        list->head->prev = NULL;
    }

    free(temp);
    pthread_mutex_unlock(&list->lock);
    return data;
}

// Check if the list is empty
int dll_is_empty(DoublyLinkedList* list) {
    pthread_mutex_lock(&list->lock);
    int is_empty = (list->head == NULL);
    pthread_mutex_unlock(&list->lock);
    return is_empty;
}

// Clear the list
void dll_clear(DoublyLinkedList* list) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }

    list->head = list->tail = NULL;

    pthread_mutex_unlock(&list->lock);
}

// Destroy the list
void dll_destroy(DoublyLinkedList* list) {
    dll_clear(list);
    pthread_mutex_destroy(&list->lock);
}

// Print the elements of the list
void dll_print(DoublyLinkedList* list) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    printf("Doubly Linked List: ");
    while (current != NULL) {
        printf("%d ", current->data);
        current = current->next;
    }
    printf("\n");

    pthread_mutex_unlock(&list->lock);
}