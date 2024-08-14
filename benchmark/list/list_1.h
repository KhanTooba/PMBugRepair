#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* head = NULL;  
pthread_mutex_t list_mutex;  


void insert(int data) {
    Node* new_node = (Node*)pmalloc(sizeof(Node));
    new_node->data = data;

    pthread_mutex_lock(&list_mutex);  
    new_node->next = head;
    head = new_node;
    pthread_mutex_unlock(&list_mutex);  
}

void* thread_func(void* arg) {
    int start = *((int*)arg);
    for (int i = start; i < start + 50; i++) {
        insert(i);
    }
    return NULL;
}
