#include <stdio.h>
#include <pthread.h>
#include "graph.h"

#define N_THREADS 2
#define N_Vertices 10

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
    for(int i=0;i<10;i++){
        addEdge(graph, rand()%N_Vertices, rand()%N_Vertices);
        hasEdge(graph, rand()%N_Vertices, rand()%N_Vertices); 
    }

    printGraph(graph);

    pthread_exit(NULL);
}

int main() {
    Graph* graph = createGraph(N_Vertices);

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

    // printGraph(graph);

    destroyGraph(graph);
    return 0;
}
