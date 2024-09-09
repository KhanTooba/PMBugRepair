#include<skipLists.h>

#define N_THREADS 2
// Thread function to perform multiple operations on the skip list
void* threadFunc(void* arg) {
    SkipList* skipList = (SkipList*)arg;

    // Write-after-write dependency managed at the thread level
    insert(skipList, 10);
    insert(skipList, 20);
    delete_element(skipList, 10);
    insert(skipList, 30);

    return NULL;
}

int main() {
    // Create the skip list
    SkipList* skipList = createSkipList();

    // Create threads
    pthread_t threads[N_THREADS];
    for (int i = 0; i < N_THREADS; i++) {
        pthread_create(&threads[i], NULL, threadFunc, (void*)skipList);
    }

    // Join threads
    for (int i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Print the skip list after thread operations
    printSkipList(skipList);

    return 0;
}
