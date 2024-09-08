/*
 * Linked List Data Structure in C with Multithreading
 *
 * This implementation of the linked list data structure is part of **ThreadTrove**, 
 * a collection of lock-based concurrent data structures written in C. The linked 
 * list is designed to be thread-safe, allowing multiple threads to perform operations 
 * concurrently while preventing data corruption. Synchronization is achieved using 
 * mutex locks to control access to shared data, ensuring safe concurrent insertions, 
 * deletions, searches, and updates.
 *
 * In this implementation, threads can introduce read-write dependencies through 
 * the `thread_func` function and the `main` method. However, the internal linked 
 * list functions are unaware of these dependencies, ensuring that the data 
 * structure's core logic remains independent and reliable.
 *
 * Functions:
 * 
 * - `void init_list(LinkedList* list)`:
 *     Initializes the linked list by setting the head to NULL and initializing 
 *     the mutex lock to enable thread-safe access.
 *
 * - `void insert(LinkedList* list, int value)`:
 *     Inserts a new node with the specified value at the beginning of the list. 
 *     This function is protected by a mutex lock to ensure thread safety.
 *
 * - `bool delete_from_list(LinkedList* list, int value)`:
 *     Deletes the first occurrence of the specified value from the list. 
 *     If the value is found, it is removed from the list. Returns true if the deletion 
 *     is successful, false if the value is not found. This function is protected by a mutex lock.
 *
 * - `Node* search(LinkedList* list, int value)`:
 *     Searches for the first node with the specified value in the list. 
 *     If the value is found, the pointer to the node is returned; otherwise, NULL is returned. 
 *     The function ensures thread-safe access using a mutex lock.
 *
 * - `void update(LinkedList* list, int old_value, int new_value)`:
 *     Updates the first occurrence of the specified `old_value` in the list 
 *     to the new value `new_value`. If the `old_value` is not found, the function does nothing. 
 *     It uses a mutex lock to ensure thread-safe access.
 *
 * - `bool contains(LinkedList* list, int value)`:
 *     Checks if the specified value exists in the list. Returns true if 
 *     the value is found, false otherwise. The function is protected by a mutex lock.
 *
 * - `void clear(LinkedList* list)`:
 *     Clears the linked list by removing all nodes and freeing associated memory. 
 *     This function is thread-safe due to the use of a mutex lock.
 *
 * - `int size(LinkedList* list)`:
 *     Returns the number of nodes currently in the list. 
 *     Ensures thread safety using a mutex lock.
 *
 * - `bool is_empty(LinkedList* list)`:
 *     Checks if the linked list is empty by comparing its size to zero. 
 *     Thread-safe due to a mutex lock.
 *
 * - `void display(LinkedList* list)`:
 *     Prints the contents of the linked list to the console, showing each node's 
 *     value in sequence. The function locks the list to ensure correct data display 
 *     in a multithreaded environment.
 *
 * - `void reverse(LinkedList* list)`:
 *     Reverses the order of nodes in the linked list. Ensures thread safety 
 *     using a mutex lock.
 *
 * - `void append(LinkedList* list, int value)`:
 *     Inserts a new node with the specified value at the end of the list. 
 *     This function is protected by a mutex lock.
 *
 * - `void insert_after(LinkedList* list, int target, int value)`:
 *     Inserts a new node with the specified value after the first occurrence 
 *     of `target` in the list. This function ensures thread safety with a mutex lock.
 * 
 * This linked list implementation is part of the **ThreadTrove** collection, which provides 
 * a variety of lock-based concurrent data structures in C, designed to handle 
 * multithreading scenarios efficiently.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>  // For sleep function
#include "pm.h"

// Node structure for the linked list
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Linked list structure
typedef struct LinkedList {
    Node* head;
    int size;
    pthread_mutex_t lock;
} LinkedList;

// Initialize the linked list
void init_list(LinkedList* list) {
    list->head = NULL;
    list->size = 0;
    pthread_mutex_init(&list->lock, NULL);
}

// Insert a new node at the beginning of the list
void insert(LinkedList* list, int value) {
    pthread_mutex_lock(&list->lock);

    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = value;
    new_node->next = list->head;
    list->head = new_node;
    list->size++;

    pthread_mutex_unlock(&list->lock);
}

// Delete the first occurrence of the specified value from the list
bool delete_from_list(LinkedList* list, int value) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    Node* prev = NULL;

    while (current != NULL && current->data != value) {
        prev = current;
        current = current->next;
    }

    if (current == NULL) {
        pthread_mutex_unlock(&list->lock);
        return false;  // Value not found
    }

    if (prev == NULL) {
        list->head = current->next;
    } else {
        prev->next = current->next;
    }

    free(current);
    list->size--;

    pthread_mutex_unlock(&list->lock);
    return true;
}

// Search for the first node with the specified value
Node* search(LinkedList* list, int value) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    while (current != NULL) {
        if (current->data == value) {
            pthread_mutex_unlock(&list->lock);
            return current;  // Value found
        }
        current = current->next;
    }

    pthread_mutex_unlock(&list->lock);
    return NULL;  // Value not found
}

// Update the first occurrence of the specified old_value to new_value
void update(LinkedList* list, int old_value, int new_value) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    while (current != NULL) {
        if (current->data == old_value) {
            current->data = new_value;
            pthread_mutex_unlock(&list->lock);
            return;
        }
        current = current->next;
    }

    pthread_mutex_unlock(&list->lock);
}

// Check if the specified value exists in the list
bool contains(LinkedList* list, int value) {
    return search(list, value) != NULL;
}

// Clear the linked list by removing all nodes
void clear(LinkedList* list) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    while (current != NULL) {
        Node* to_free = current;
        current = current->next;
        free(to_free);
    }
    list->head = NULL;
    list->size = 0;

    pthread_mutex_unlock(&list->lock);
}

// Get the current size of the list
int size(LinkedList* list) {
    pthread_mutex_lock(&list->lock);
    int current_size = list->size;
    pthread_mutex_unlock(&list->lock);
    return current_size;
}

// Check if the linked list is empty
bool is_empty(LinkedList* list) {
    return size(list) == 0;
}

// Display the contents of the linked list
void display(LinkedList* list) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    printf("List: ");
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\n");

    pthread_mutex_unlock(&list->lock);
}

// Reverse the order of nodes in the linked list
void reverse(LinkedList* list) {
    pthread_mutex_lock(&list->lock);

    Node* prev = NULL;
    Node* current = list->head;
    Node* next = NULL;
    while (current != NULL) {
        next = current->next;
        current->next = prev;
        prev = current;
        current = next;
    }
    list->head = prev;

    pthread_mutex_unlock(&list->lock);
}

// Insert a new node at the end of the list
void append(LinkedList* list, int value) {
    pthread_mutex_lock(&list->lock);

    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = value;
    new_node->next = NULL;

    if (list->head == NULL) {
        list->head = new_node;
    } else {
        Node* current = list->head;
        while (current->next != NULL) {
            current = current->next;
        }
        current->next = new_node;
    }
    list->size++;

    pthread_mutex_unlock(&list->lock);
}

// Insert a new node after the first occurrence of the target value
void insert_after(LinkedList* list, int target, int value) {
    pthread_mutex_lock(&list->lock);

    Node* current = list->head;
    while (current != NULL) {
        if (current->data == target) {
            Node* new_node = (Node*)malloc(sizeof(Node));
            new_node->data = value;
            new_node->next = current->next;
            current->next = new_node;
            list->size++;
            break;
        }
        current = current->next;
    }

    pthread_mutex_unlock(&list->lock);
}