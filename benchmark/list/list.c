#include <list_1.h>

int main() {
    pthread_t thread1, thread2;
    int start1 = 0, start2 = 50;

    pthread_mutex_init(&list_mutex, NULL);  // Initialize the mutex

    // Create two threads
    pthread_create(&thread1, NULL, thread_func, &start1);
    pthread_create(&thread2, NULL, thread_func, &start2);

    // Wait for both threads to finish
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    // Print the linked list
    Node* temp = head;
    while (temp != NULL) {
        printf("%d ", temp->data);
        temp = temp->next;
    }
    printf("\n");

    // Cleanup
    pthread_mutex_destroy(&list_mutex);
    while (head != NULL) {
        Node* temp = head;
        head = head->next;
        free(temp);
    }

    return 0;
}
