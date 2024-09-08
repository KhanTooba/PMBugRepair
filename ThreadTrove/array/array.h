/*
 * Array Data Structure in C with Multithreading
 *
 * This implementation of the array data structure is part of **ThreadTrove**, 
 * a collection of lock-based concurrent data structures written in C. The array 
 * is designed to be thread-safe, allowing multiple threads to perform operations 
 * concurrently while preventing data corruption. Synchronization is achieved using 
 * mutex locks to control access to shared data, enabling safe concurrent inserts, 
 * deletions, and updates.
 *
 * In this implementation, threads can introduce write-after-read dependencies 
 * through the `thread_func` function and the `main` method. However, the internal 
 * array functions are agnostic to these dependencies, ensuring that the data 
 * structure's core logic remains consistent and robust.
 *
 * Functions:
 * 
 * - `void init_array(Array* arr)`:
 *     Initializes the array with an initial capacity and sets the size to zero. 
 *     Also initializes the mutex lock to enable thread-safe access.
 *
 * - `void resize_array(Array* arr)`:
 *     Doubles the capacity of the array when it becomes full. Reallocates memory 
 *     to accommodate the increased capacity.
 *
 * - `void insert(Array* arr, int value)`:
 *     Inserts a new element at the end of the array. If the array is full, it 
 *     resizes first. This function is protected by a mutex lock to ensure thread safety.
 *
 * - `bool delete(Array* arr, int index)`:
 *     Deletes an element at the specified index by shifting the elements to the left. 
 *     Checks for boundary conditions and returns a boolean indicating success. 
 *     Protected by a mutex lock.
 *
 * - `int get(Array* arr, int index)`:
 *     Retrieves the element at the specified index. Returns `-1` if the index 
 *     is out of bounds. Ensures thread-safe access with a mutex lock.
 *
 * - `void update(Array* arr, int index, int value)`:
 *     Updates the element at the specified index with a new value. Checks for 
 *     boundary conditions and uses a mutex lock for thread-safe access.
 *
 * - `int find(Array* arr, int value)`:
 *     Searches for an element in the array and returns its index if found, 
 *     or `-1` if not found. Protected by a mutex lock.
 *
 * - `void clear(Array* arr)`:
 *     Clears the array by resetting its size to zero. This function is thread-safe 
 *     due to the use of a mutex lock.
 *
 * - `int size(Array* arr)`:
 *     Returns the current size of the array. Ensures thread safety using a mutex lock.
 *
 * - `bool is_empty(Array* arr)`:
 *     Checks if the array is empty by comparing its size to zero. 
 *     Thread-safe due to a mutex lock.
 *
 * - `int capacity(Array* arr)`:
 *     Returns the current capacity of the array. Protected by a mutex lock 
 *     for thread-safe access.
 *
 * - `void display(Array* arr)`:
 *     Prints the contents of the array to the console. Locks the array to 
 *     ensure correct data display in a multithreaded environment.
 *
 * - `void sort(Array* arr)`:
 *     Sorts the array in ascending order using a simple bubble sort algorithm. 
 *     Thread-safe due to the use of a mutex lock.
 *
 * - `void reverse(Array* arr)`:
 *     Reverses the elements of the array in place. Protected by a mutex lock 
 *     to ensure thread-safe operation.
 *
 * - `void merge(Array* arr, Array* other)`:
 *     Merges another array into the current array by inserting each element 
 *     of the other array. Ensures thread safety with a mutex lock.
 *
 * This array implementation is part of the **ThreadTrove** collection, which provides 
 * a variety of lock-based concurrent data structures in C, designed to handle 
 * multithreading scenarios efficiently.
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include "pm.h"
#define INITIAL_CAPACITY 10  // Initial capacity of the array

// Array structure
typedef struct {
    int* data;              // Pointer to the array elements
    int size;               // Current number of elements in the array
    int capacity;           // Current capacity of the array
    pthread_mutex_t lock;   // Mutex lock for thread-safe access
} Array;

// Function to initialize the array
void init_array(Array* arr) {
    arr->data = (int*)malloc(INITIAL_CAPACITY * sizeof(int));  // Allocate memory
    arr->size = 0;  // Initialize size to 0
    arr->capacity = INITIAL_CAPACITY;  // Set initial capacity
    pthread_mutex_init(&arr->lock, NULL);  // Initialize the mutex lock
}

// Function to resize the array when it's full
void resize_array(Array* arr) {
    arr->capacity *= 2;  // Double the capacity
    arr->data = (int*)realloc(arr->data, arr->capacity * sizeof(int));  // Reallocate memory
}

// Function to insert an element at the end of the array
void insert(Array* arr, int value) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    // Resize the array if it's full
    if (arr->size == arr->capacity) {
        resize_array(arr);
    }

    arr->data[arr->size] = value;  // Add the element to the array
    arr->size++;  // Increment the size

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after insertion
}

// Function to delete an element from the array
bool delete_element(Array* arr, int index) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    if (index < 0 || index >= arr->size) {
        pthread_mutex_unlock(&arr->lock);  // Unlock if the index is out of bounds
        return false;  // Invalid index, deletion failed
    }

    // Shift elements to the left to fill the gap
    for (int i = index; i < arr->size - 1; i++) {
        arr->data[i] = arr->data[i + 1];
    }

    arr->size--;  // Decrement the size

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after deletion
    return true;  // Deletion successful
}

// Function to get an element at a specific index
int get(Array* arr, int index) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    if (index < 0 || index >= arr->size) {
        pthread_mutex_unlock(&arr->lock);  // Unlock if the index is out of bounds
        return -1;  // Invalid index, return -1
    }

    int value = arr->data[index];  // Get the element

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after getting the element
    return value;  // Return the element
}

// Function to update an element at a specific index
bool update(Array* arr, int index, int value) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    if (index < 0 || index >= arr->size) {
        pthread_mutex_unlock(&arr->lock);  // Unlock if the index is out of bounds
        return false;  // Invalid index, update failed
    }

    arr->data[index] = value;  // Update the element

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after updating
    return true;  // Update successful
}

// Function to find an element in the array
int find(Array* arr, int value) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    for (int i = 0; i < arr->size; i++) {
        if (arr->data[i] == value) {
            pthread_mutex_unlock(&arr->lock);  // Unlock if the element is found
            return i;  // Return the index of the found element
        }
    }

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after searching
    return -1;  // Element not found
}

// Function to clear the array
void clear(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    arr->size = 0;  // Reset the size

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after clearing
}

// Function to get the size of the array
int size(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    int size = arr->size;  // Get the size

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after getting the size
    return size;  // Return the size
}

// Function to check if the array is empty
bool is_empty(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    bool empty = (arr->size == 0);  // Check if the array is empty

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after checking
    return empty;  // Return whether the array is empty
}

// Function to get the capacity of the array
int capacity(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    int capacity = arr->capacity;  // Get the capacity

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after getting the capacity
    return capacity;  // Return the capacity
}

// Function to display the contents of the array
void display(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    printf("Array contents: ");
    for (int i = 0; i < arr->size; i++) {
        printf("%d ", arr->data[i]);  // Print each element
    }
    printf("\n");

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after displaying
}

// Function to sort the array in ascending order
void sort(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    // Simple bubble sort algorithm
    for (int i = 0; i < arr->size - 1; i++) {
        for (int j = 0; j < arr->size - 1 - i; j++) {
            if (arr->data[j] > arr->data[j + 1]) {
                int temp = arr->data[j];
                arr->data[j] = arr->data[j + 1];
                arr->data[j + 1] = temp;
            }
        }
    }

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after sorting
}

// Function to reverse the array
void reverse(Array* arr) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    int start = 0;
    int end = arr->size - 1;

    while (start < end) {
        // Swap elements at start and end
        int temp = arr->data[start];
        arr->data[start] = arr->data[end];
        arr->data[end] = temp;

        start++;
        end--;
    }

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after reversing
}

// Function to merge another array into the current array
void merge(Array* arr, Array* other) {
    pthread_mutex_lock(&arr->lock);  // Lock the array for thread safety

    for (int i = 0; i < other->size; i++) {
        insert(arr, other->data[i]);  // Insert each element of the other array
    }

    pthread_mutex_unlock(&arr->lock);  // Unlock the array after merging
}
