#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"
// Linked list node
typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* head = NULL;  // Shared linked list head
pthread_mutex_t list_mutex;  // Mutex to protect the linked list

// Function to insert a node at the beginning of the list
void insert(int data) {
    Node* new_node = (Node*)pmalloc(sizeof(Node));
    new_node->data = data;

    pthread_mutex_lock(&list_mutex);  // Lock the mutex
    new_node->next = head;
    head = new_node;
    pthread_mutex_unlock(&list_mutex);  // Unlock the mutex
}

// Thread function
void* thread_func(void* arg) {
    int start = *((int*)arg);
    for (int i = start; i < start + 50; i++) {
        insert(i);
    }
    return NULL;
}
