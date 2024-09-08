#include <stdio.h>
#include <pthread.h>
#include "graph.h"

#define N_THREADS 2

typedef struct {
    Graph *graph;
    int thread_id;
} ThreadData;

// Function for threads to run
void* threadFunction(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    Graph* graph = data->graph;
    int thread_id = data->thread_id;

    // Example of write-after-write dependency
    if (thread_id == 0) {
        addEdge(graph, 0, 1);
        addEdge(graph, 0, 2);
    } else {
        addEdge(graph, 1, 2);
        addEdge(graph, 2, 3);
    }

    printGraph(graph);

    pthread_exit(NULL);
}

int main() {
    Graph* graph = createGraph(4);

    pthread_t threads[N_THREADS];
    ThreadData thread_data[N_THREADS];

    // Create threads
    for (int i = 0; i < N_THREADS; i++) {
        thread_data[i].graph = graph;
        thread_data[i].thread_id = i;
        pthread_create(&threads[i], NULL, threadFunction, &thread_data[i]);
    }

    // Join threads
    for (int i = 0; i < N_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // Example of write-after-write dependency in main
    addEdge(graph, 3, 0);
    addEdge(graph, 1, 3);

    printGraph(graph);

    destroyGraph(graph);
    return 0;
}
