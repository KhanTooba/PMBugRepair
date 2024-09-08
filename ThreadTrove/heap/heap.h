/*
 * Heap Data Structure with Multithreading Support
 * 
 * This is a part of a collection of lock-based data structures written in C.
 * 
 * This implementation provides a min-heap data structure that supports concurrent 
 * access using multithreading. The heap is protected by a mutex, ensuring that 
 * operations on the heap are thread-safe. The heap is implemented as an array, 
 * with standard heap operations such as insert and extract min. The internal 
 * functions of the heap are designed to be unaware of any multithreading 
 * dependencies, allowing them to be used independently of the locking mechanism.
 * 
 * Functions:
 * 
 * - Heap* createHeap(int capacity):
 *      Creates and initializes a heap with the given capacity. Allocates memory 
 *      for the heap structure and the underlying array. Initializes the mutex 
 *      used for locking. Returns a pointer to the newly created heap.
 * 
 * - void destroyHeap(Heap* heap):
 *      Destroys the heap by freeing the allocated memory for the array and 
 *      heap structure. Also destroys the mutex used for locking.
 * 
 * - void insertHeap(Heap* heap, int value):
 *      Inserts a value into the heap while maintaining the min-heap property. 
 *      The function locks the heap before performing the insertion and unlocks 
 *      it after the operation is complete. If the heap is full, it prints a 
 *      "Heap overflow" message.
 * 
 * - int extractMin(Heap* heap):
 *      Removes and returns the minimum element from the heap. The function locks 
 *      the heap before performing the extraction and unlocks it after the operation 
 *      is complete. If the heap is empty, it returns -1.
 * 
 * - int getMin(Heap* heap):
 *      Returns the minimum element from the heap without removing it. The function 
 *      locks the heap before accessing the minimum element and unlocks it after 
 *      the operation is complete. If the heap is empty, it returns -1.
 * 
 * - int isEmpty(Heap* heap):
 *      Checks if the heap is empty. The function locks the heap before checking 
 *      the size and unlocks it after the operation is complete. Returns 1 if the 
 *      heap is empty, otherwise returns 0.
 * 
 * - void heapify(Heap* heap, int i):
 *      Heapifies the subtree rooted at index i to maintain the min-heap property. 
 *      This function is called internally by other functions and does not lock 
 *      the heap, as it is expected to be called only within locked sections.
 * 
 * - void printHeap(Heap* heap):
 *      Prints the contents of the heap. The function locks the heap before accessing 
 *      the array and unlocks it after printing.
 * 
 * Usage:
 * 
 * The heap data structure is used in a multithreaded environment where multiple 
 * threads can perform operations on the heap concurrently. The write-after-write 
 * dependencies are handled outside the internal heap functions, specifically 
 * within the thread functions and the main function. This allows the heap to be 
 * used safely across different threads without modifying the core heap logic.
 */

#ifndef HEAP_H
#define HEAP_H
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pm.h"

// Heap structure
typedef struct {
    int *array;
    int capacity;
    int size;
    pthread_mutex_t lock;
} Heap;

// Function prototypes
Heap* createHeap(int capacity);
void destroyHeap(Heap* heap);
void insertHeap(Heap* heap, int value);
int extractMin(Heap* heap);
int getMin(Heap* heap);
int isEmpty(Heap* heap);
void heapify(Heap* heap, int i);
void printHeap(Heap* heap);

#endif // HEAP_H

// Function to create a heap
Heap* createHeap(int capacity) {
    Heap* heap = (Heap*)pmalloc(sizeof(Heap));
    heap->array = (int*)pmalloc(capacity * sizeof(int));
    heap->capacity = capacity;
    heap->size = 0;
    pthread_mutex_init(&heap->lock, NULL);
    return heap;
}

// Function to destroy a heap
void destroyHeap(Heap* heap) {
    free(heap->array);
    pthread_mutex_destroy(&heap->lock);
    free(heap);
}

// Function to insert a value into the heap
void insertHeap(Heap* heap, int value) {
    pthread_mutex_lock(&heap->lock);

    if (heap->size == heap->capacity) {
        printf("Heap overflow\n");
        pthread_mutex_unlock(&heap->lock);
        return;
    }

    // Insert the new element at the end of the array
    heap->size++;
    int i = heap->size - 1;
    heap->array[i] = value;

    // Fix the min heap property if it's violated
    while (i != 0 && heap->array[(i - 1) / 2] > heap->array[i]) {
        int temp = heap->array[i];
        heap->array[i] = heap->array[(i - 1) / 2];
        heap->array[(i - 1) / 2] = temp;
        i = (i - 1) / 2;
    }

    pthread_mutex_unlock(&heap->lock);
}

// Function to extract the minimum value from the heap
int extractMin(Heap* heap) {
    pthread_mutex_lock(&heap->lock);

    if (heap->size <= 0) {
        pthread_mutex_unlock(&heap->lock);
        return -1; // Heap is empty
    }
    if (heap->size == 1) {
        heap->size--;
        pthread_mutex_unlock(&heap->lock);
        return heap->array[0];
    }

    // Store the minimum value and remove it from the heap
    int root = heap->array[0];
    heap->array[0] = heap->array[heap->size - 1];
    heap->size--;
    heapify(heap, 0);

    pthread_mutex_unlock(&heap->lock);
    return root;
}

// Function to get the minimum value from the heap
int getMin(Heap* heap) {
    pthread_mutex_lock(&heap->lock);

    if (heap->size <= 0) {
        pthread_mutex_unlock(&heap->lock);
        return -1; // Heap is empty
    }

    int min = heap->array[0];

    pthread_mutex_unlock(&heap->lock);
    return min;
}

// Function to check if the heap is empty
int isEmpty(Heap* heap) {
    pthread_mutex_lock(&heap->lock);
    int empty = (heap->size == 0);
    pthread_mutex_unlock(&heap->lock);
    return empty;
}

// Function to heapify a subtree with root at index i
void heapify(Heap* heap, int i) {
    int smallest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < heap->size && heap->array[left] < heap->array[smallest]) {
        smallest = left;
    }
    if (right < heap->size && heap->array[right] < heap->array[smallest]) {
        smallest = right;
    }
    if (smallest != i) {
        int temp = heap->array[i];
        heap->array[i] = heap->array[smallest];
        heap->array[smallest] = temp;
        heapify(heap, smallest);
    }
}

// Function to print the heap elements
void printHeap(Heap* heap) {
    pthread_mutex_lock(&heap->lock);

    for (int i = 0; i < heap->size; i++) {
        printf("%d ", heap->array[i]);
    }
    printf("\n");

    pthread_mutex_unlock(&heap->lock);
}
