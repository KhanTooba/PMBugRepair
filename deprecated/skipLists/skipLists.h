/*
 * Skip List Data Structure (Lock-Based Implementation)
 *
 * This skip list is part of a collection of lock-based data structures written in C.
 * It provides an efficient way to perform search, insert, and delete operations
 * in an ordered sequence of elements using multiple levels of linked lists.
 * This implementation supports multithreading with proper locking mechanisms to
 * ensure thread safety during concurrent operations.
 *
 * The skip list uses a probabilistic approach to maintain an average time complexity
 * of O(log n) for search, insert, and delete operations. It allows fast traversal of the
 * list by "skipping" over large sections, facilitated by multiple levels of linked lists.
 *
 * Functions:
 *
 * 1. SkipListNode* createNode(int level, int key):
 *    - Creates a new skip list node with the specified level and key.
 *    - Initializes the forward pointers of the node to NULL.
 *
 * 2. SkipList* createSkipList():
 *    - Creates a new skip list structure.
 *    - Initializes the header node with the minimum possible key (INT_MIN) and the highest level.
 *    - Initializes a global lock to ensure thread safety during operations.
 *
 * 3. int randomLevel():
 *    - Generates a random level for a new node to be inserted in the skip list.
 *    - The level is determined based on a probabilistic approach with a fixed probability (0.5).
 *
 * 4. void insert(SkipList* skipList, int key):
 *    - Inserts a key into the skip list at the appropriate position.
 *    - Updates the pointers at each relevant level.
 *    - Uses locks to ensure thread safety during insertion.
 *
 * 5. int search(SkipList* skipList, int key):
 *    - Searches for a key in the skip list.
 *    - Returns 1 if the key is found, otherwise returns 0.
 *    - Uses locks to ensure thread safety during search operations.
 *
 * 6. void delete(SkipList* skipList, int key):
 *    - Deletes a key from the skip list by updating the pointers at each relevant level.
 *    - Frees the memory of the removed node.
 *    - Uses locks to ensure thread safety during deletion.
 *
 * 7. void printSkipList(SkipList* skipList):
 *    - Prints the structure of the skip list at each level.
 *    - Displays the keys in the skip list from the highest level to the lowest level.
 *    - Uses locks to ensure thread safety during printing.
 *
 * This skip list is designed to be flexible, efficient, and thread-safe, making it suitable for use in concurrent environments
 * where multiple threads may perform operations on the data structure simultaneously.
 */


#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <limits.h>
#include "pm.h"
// Constants
#define MAX_LEVEL 6
#define PROBABILITY 0.5

// Skip List Node Structure
typedef struct SkipListNode {
    int key;
    struct SkipListNode** forward; // Array of pointers to nodes at different levels
} SkipListNode;

// Skip List Structure
typedef struct SkipList {
    int level;  // Current level of the skip list
    SkipListNode* header;  // Header node (dummy node)
    pthread_mutex_t lock;  // Global lock for thread safety
} SkipList;

// Helper Function to Create a New Node
SkipListNode* createNode(int level, int key) {
    SkipListNode* node = (SkipListNode*)pmalloc(sizeof(SkipListNode));
    node->key = key;
    node->forward = (SkipListNode**)pmalloc((level + 1) * sizeof(SkipListNode*));
    for (int i = 0; i <= level; i++) {
        node->forward[i] = NULL;
    }
    return node;
}

// Helper Function to Create a Skip List
SkipList* createSkipList() {
    SkipList* skipList = (SkipList*)pmalloc(sizeof(SkipList));
    skipList->level = 0;
    skipList->header = createNode(MAX_LEVEL, INT_MIN);  // Header node with minimum possible key
    pthread_mutex_init(&skipList->lock, NULL);  // Initialize the global lock
    return skipList;
}

// Helper Function to Generate a Random Level
int randomLevel() {
    int level = 0;
    while (((double)rand() / RAND_MAX) < PROBABILITY && level < MAX_LEVEL) {
        level++;
    }
    return level;
}

// Function to Insert a Key into the Skip List
void insert(SkipList* skipList, int key) {
    SkipListNode* update[MAX_LEVEL + 1];
    SkipListNode* current = skipList->header;

    // Lock the skip list for thread safety
    pthread_mutex_lock(&skipList->lock);

    // Traverse the skip list and keep track of nodes that need to be updated
    for (int i = skipList->level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    // Move to the next node at level 0
    current = current->forward[0];

    // If the key is not already present, insert it
    if (current == NULL || current->key != key) {
        int level = randomLevel();

        // If the random level is greater than the current level of the skip list, update the list level
        if (level > skipList->level) {
            for (int i = skipList->level + 1; i <= level; i++) {
                update[i] = skipList->header;
            }
            skipList->level = level;
        }

        // Create a new node and insert it at the appropriate positions
        SkipListNode* newNode = createNode(level, key);
        for (int i = 0; i <= level; i++) {
            newNode->forward[i] = update[i]->forward[i];
            update[i]->forward[i] = newNode;
        }
    }

    // Unlock the skip list
    pthread_mutex_unlock(&skipList->lock);
}

// Function to Search for a Key in the Skip List
int search(SkipList* skipList, int key) {
    SkipListNode* current = skipList->header;

    // Lock the skip list for thread safety
    pthread_mutex_lock(&skipList->lock);

    // Traverse the skip list
    for (int i = skipList->level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
    }

    // Move to the next node at level 0
    current = current->forward[0];

    // Unlock the skip list
    pthread_mutex_unlock(&skipList->lock);

    // Check if the key was found
    if (current != NULL && current->key == key) {
        return 1;  // Key found
    } else {
        return 0;  // Key not found
    }
}

// Function to Delete a Key from the Skip List
void delete_element(SkipList* skipList, int key) {
    SkipListNode* update[MAX_LEVEL + 1];
    SkipListNode* current = skipList->header;

    // Lock the skip list for thread safety
    pthread_mutex_lock(&skipList->lock);

    // Traverse the skip list and keep track of nodes that need to be updated
    for (int i = skipList->level; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    // Move to the next node at level 0
    current = current->forward[0];

    // If the key is found, remove it
    if (current != NULL && current->key == key) {
        for (int i = 0; i <= skipList->level; i++) {
            if (update[i]->forward[i] != current) {
                break;
            }
            update[i]->forward[i] = current->forward[i];
        }

        // Free the memory of the removed node
        free(current);

        // Update the level of the skip list if necessary
        while (skipList->level > 0 && skipList->header->forward[skipList->level] == NULL) {
            skipList->level--;
        }
    }

    // Unlock the skip list
    pthread_mutex_unlock(&skipList->lock);
}

// Function to Print the Skip List
void printSkipList(SkipList* skipList) {
    // Lock the skip list for thread safety
    pthread_mutex_lock(&skipList->lock);

    printf("Skip List:\n");
    for (int i = 0; i <= skipList->level; i++) {
        SkipListNode* node = skipList->header->forward[i];
        printf("Level %d: ", i);
        while (node != NULL) {
            printf("%d -> ", node->key);
            node = node->forward[i];
        }
        printf("NULL\n");
    }

    // Unlock the skip list
    pthread_mutex_unlock(&skipList->lock);
}