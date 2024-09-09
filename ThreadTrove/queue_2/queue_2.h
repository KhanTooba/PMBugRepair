#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
//#inlcude “pm.h”
#include "pm.h"

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* front = NULL; 
Node* rear = NULL;   
pthread_mutex_t queue_mutex; 

void enqueue(int data) {
    Node* new_node = (Node*)pmalloc(sizeof(Node));
    if (new_node == NULL) {
        perror("Failed to allocate memory");
        exit(EXIT_FAILURE);
    }
    new_node->data = data;
    new_node->next = NULL;

    pthread_mutex_lock(&queue_mutex);  

    if (rear == NULL) { 
        front = rear = new_node;
    } else {
        rear->next = new_node;
        rear = new_node;
    }

    pthread_mutex_unlock(&queue_mutex);  
}

int dequeue() {
    pthread_mutex_lock(&queue_mutex);  

    if (front == NULL) {  
        pthread_mutex_unlock(&queue_mutex);
        return -1;
    }

    Node* temp = front;
    int dequeued_value = front->data;
    front = front->next;

    if (front == NULL) {
        rear = NULL;
    }

    pthread_mutex_unlock(&queue_mutex);  

    free(temp);
    return dequeued_value;
}

void* thread_func(void* arg) {
    for (int i = 0; i < 25; i++) {
        int value = dequeue();
        if (value != -1) {
            printf("Thread %ld dequeued: %d\n", pthread_self(), value);
            enqueue(value);
            printf("Thread %ld enqueued: %d\n", pthread_self(), value);
        } else {
            printf("Thread %ld found the queue empty\n", pthread_self());
        }
    }

    return NULL;
}
