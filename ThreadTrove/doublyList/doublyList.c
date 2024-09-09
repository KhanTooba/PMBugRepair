#include<doublyList.h>
#define N_THREADS 2

// Thread function to introduce write-after-write dependency
void* thread_func(void* arg) {
    DoublyLinkedList* list = (DoublyLinkedList*)arg;

    // Thread performs multiple operations on the list
    int value = dll_remove_start(list);
    dll_insert_end(list, value + 1);
    dll_insert_start(list, value + 2);
    dll_remove_end(list);

    return NULL;
}

int main() {
    DoublyLinkedList list;
    dll_init(&list);

    // Insert initial values
    dll_insert_end(&list, 1);
    dll_insert_end(&list, 2);
    dll_insert_end(&list, 3);

    pthread_t threads[N_THREADS];

    // Create threads
    for (int i = 0; i < N_THREADS; ++i) {
        pthread_create(&threads[i], NULL, thread_func, (void*)&list);
    }

    // Wait for threads to finish
    for (int i = 0; i < N_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Print final state of the list
    dll_print(&list);

    dll_destroy(&list);
    return 0;
}
