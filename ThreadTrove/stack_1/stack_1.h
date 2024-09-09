/*
 * Stack Data Structure Implementation in C
 *
 * This implementation of the Stack data structure is part of a collection of 
 * lock-based data structures written in C. The stack is designed for concurrent 
 * access using mutex locks, allowing multiple threads to perform operations on 
 * the stack simultaneously. The stack supports various operations such as push, 
 * pop, peek, and size retrieval, while ensuring thread safety through proper 
 * synchronization mechanisms. The internal functions of the stack do not handle 
 * thread dependencies, keeping the design modular and clean. 
 *
 * Functions:
 * 
 * - void stack_init(Stack* stack):
 *   Initializes the stack by setting the top index to -1 and initializing the 
 *   mutex lock for thread synchronization.
 *
 * - int stack_is_empty(Stack* stack):
 *   Checks if the stack is empty by comparing the top index to -1. Returns 1 
 *   if the stack is empty, 0 otherwise.
 *
 * - int stack_is_full(Stack* stack):
 *   Checks if the stack is full by comparing the top index to the maximum 
 *   capacity (STACK_CAPACITY - 1). Returns 1 if the stack is full, 0 otherwise.
 *
 * - void stack_push(Stack* stack, int value):
 *   Pushes a new element onto the stack. If the stack is full, it prints an 
 *   overflow error message. This function locks the stack before the operation 
 *   and unlocks it afterward to ensure thread safety.
 *
 * - int stack_pop(Stack* stack):
 *   Pops the top element from the stack. If the stack is empty, it prints an 
 *   underflow error message and returns -1. This function locks the stack 
 *   before the operation and unlocks it afterward to ensure thread safety.
 *
 * - int stack_peek(Stack* stack):
 *   Returns the top element of the stack without removing it. If the stack 
 *   is empty, it prints an error message and returns -1. This function locks 
 *   the stack before the operation and unlocks it afterward.
 *
 * - int stack_size(Stack* stack):
 *   Returns the current number of elements in the stack by adding 1 to the top 
 *   index. This function locks the stack before the operation and unlocks it 
 *   afterward.
 *
 * - void stack_clear(Stack* stack):
 *   Clears the stack by setting the top index to -1. This function locks the 
 *   stack before the operation and unlocks it afterward.
 *
 * - void stack_destroy(Stack* stack):
 *   Destroys the mutex lock associated with the stack. This function should 
 *   be called when the stack is no longer needed to free resources.
 *
 * The stack is designed with a fixed capacity (STACK_CAPACITY), but it can be 
 * extended by modifying the capacity definition. This implementation handles 
 * edge cases such as overflow and underflow, providing a robust and thread-safe 
 * stack data structure.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"
// Node structure for linked list
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Stack structure using a linked list
typedef struct Stack {
    Node* top;
    pthread_mutex_t lock;  // Lock for thread synchronization
} Stack;

// Initialize the stack
void stack_init(Stack* stack) {
    stack->top = NULL;
    pthread_mutex_init(&(stack->lock), NULL);
}

// Check if the stack is empty
int stack_is_empty(Stack* stack) {
    return stack->top == NULL;
}

// Push an element onto the stack
void stack_push(Stack* stack, int value) {
    pthread_mutex_lock(&(stack->lock));  // Lock for safe concurrent access
    
    Node* new_node = (Node*)pmalloc(sizeof(Node));
    if (new_node == NULL) {
        printf("Memory allocation failed\n");
        pthread_mutex_unlock(&(stack->lock));  // Unlock before returning
        return;
    }
    
    new_node->data = value;
    new_node->next = stack->top;
    stack->top = new_node;
    printf("Pushed %d\n", value);

    pthread_mutex_unlock(&(stack->lock));  // Unlock after the operation
}

// Pop an element from the stack
int stack_pop(Stack* stack) {
    pthread_mutex_lock(&(stack->lock));  // Lock for safe concurrent access
    
    if (stack_is_empty(stack)) {
        pthread_mutex_unlock(&(stack->lock));  // Unlock before returning
        printf("Stack underflow\n");
        return -1;  // Indicate underflow
    }
    
    Node* temp = stack->top;
    int value = temp->data;
    stack->top = temp->next;
    free(temp);
    
    printf("Popped %d\n", value);

    pthread_mutex_unlock(&(stack->lock));  // Unlock after the operation
    return value;
}

// Peek the top element of the stack
int stack_peek(Stack* stack) {
    pthread_mutex_lock(&(stack->lock));  // Lock for safe concurrent access
    
    if (stack_is_empty(stack)) {
        pthread_mutex_unlock(&(stack->lock));  // Unlock before returning
        printf("Stack is empty\n");
        return -1;  // Indicate empty stack
    }
    
    int value = stack->top->data;

    pthread_mutex_unlock(&(stack->lock));  // Unlock after the operation
    return value;
}

// Get the size of the stack
int stack_size(Stack* stack) {
    pthread_mutex_lock(&(stack->lock));  // Lock for safe concurrent access
    
    int size = 0;
    Node* current = stack->top;
    while (current != NULL) {
        size++;
        current = current->next;
    }

    pthread_mutex_unlock(&(stack->lock));  // Unlock after the operation
    return size;
}

// Clear the stack
void stack_clear(Stack* stack) {
    pthread_mutex_lock(&(stack->lock));  // Lock for safe concurrent access
    
    while (!stack_is_empty(stack)) {
        Node* temp = stack->top;
        stack->top = temp->next;
        free(temp);
    }

    pthread_mutex_unlock(&(stack->lock));  // Unlock after the operation
}

// Free the stack (destroy the mutex lock)
void stack_destroy(Stack* stack) {
    pthread_mutex_destroy(&(stack->lock));
}