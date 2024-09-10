#include <stack_1.h>

// Thread function to perform stack operations with write-after-write dependency
void* thread_func(void* arg) {
    int start = rand();
    Stack* stack = (Stack*)arg;

    for (int i = start; i < start + 100; i++) {
        stack_push(stack, i);
        printf("Pushed: %d\n", i);
    }

    for (int i = 0; i < 25; i++) {
        int popped_value = stack_pop(stack);
        if (popped_value != -1) {
            printf("Popped: %d\n", popped_value);
        } else {
            printf("Stack is empty\n");
        }
    }
    int value = stack_pop(stack);  // Dependent on what another thread writes

    if (value != -1) {  // Check if pop was successful
        value += 10;  // Modify the value and push it back
        stack_push(stack, value);
    }
    return NULL;
}

int main() {
    int n_threads = 2;
    Stack stack;
    pthread_t threads[n_threads];

    // Initialize the stack
    stack_init(&stack);

    // Push some initial values
    stack_push(&stack, 5);
    stack_push(&stack, 10);

    // Create threads to perform operations with a write-after-write dependency
    for (int i = 0; i < n_threads; ++i) {
        pthread_create(&threads[i], NULL, thread_func, (void*)&stack);
    }

    // Wait for all threads to complete
    for (int i = 0; i < n_threads; ++i) {
        pthread_join(threads[i], NULL);
    }

    // Final stack state
    printf("Final stack size: %d\n", stack_size(&stack));
    while (!stack_is_empty(&stack)) {
        printf("%d\n", stack_pop(&stack));
    }

    // Destroy the stack
    stack_destroy(&stack);

    return 0;
}
