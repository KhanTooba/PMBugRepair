#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

typedef struct Node {
    int data;
    struct Node* next;
} Node;

Node* top = NULL;  
pthread_mutex_t stack_mutex;  

void push(int data) {
    Node* new_node = (Node*)pmalloc(sizeof(Node));
    if (new_node == NULL) {
        perror("Failed to allocate memory");
        exit(EXIT_FAILURE);
    }
    new_node->data = data;

    pthread_mutex_lock(&stack_mutex); 
    new_node->next = top;
    top = new_node;
    pthread_mutex_unlock(&stack_mutex);  
}

int pop() {
    pthread_mutex_lock(&stack_mutex);  
    if (top == NULL) {
        pthread_mutex_unlock(&stack_mutex); 
        return -1;  
    }
    Node* temp = top;
    int popped_value = top->data;
    top = top->next;
    pthread_mutex_unlock(&stack_mutex);  

    free(temp);
    return popped_value;
}

void* push_thread_func(void* arg) {
    int start = *((int*)arg);
    for (int i = start; i < start + 50; i++) {
        push(i);
        printf("Pushed: %d\n", i);
    }
    return NULL;
}

void* pop_thread_func(void* arg) {
    for (int i = 0; i < 50; i++) {
        int popped_value = pop();
        if (popped_value != -1) {
            printf("Popped: %d\n", popped_value);
        } else {
            printf("Stack is empty\n");
        }
    }
    return NULL;
}

