#include<skipLists.h>

#define N_THREADS 2
// Thread function to perform multiple operations on the skip list
void* threadFunc(void* arg) {
    SkipList* skipList = (SkipList*)arg;

    // Write-after-write dependency managed at the thread level
    for(int i = 0; i<50; i++){
        int value = rand()%100;
        insert(skipList, value);
        insert(skipList, value*2);
        delete_element(skipList, value);
        insert(skipList, value*3);
    }
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
