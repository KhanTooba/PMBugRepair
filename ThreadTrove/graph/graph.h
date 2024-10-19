#ifndef GRAPH_H
#define GRAPH_H
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include "pm.h"

typedef struct Node {
    int vertex;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
    pthread_mutex_t lock; 
} AdjList;

typedef struct {
    int numVertices;
    AdjList* array;
    pthread_mutex_t graph_lock; 
} Graph;

Graph* createGraph(int vertices);
void destroyGraph(Graph* graph);
void addEdge(Graph* graph, int src, int dest);
void removeEdge(Graph* graph, int src, int dest);
void printGraph(Graph* graph);
int hasEdge(Graph* graph, int src, int dest);

#endif 

Graph* createGraph(int vertices) {
    Graph* graph = (Graph*)pmalloc(sizeof(Graph));
    graph->numVertices = vertices;
    graph->array = (AdjList*)pmalloc(vertices * sizeof(AdjList));

    // Initialize each adjacency list and mutexes
    for (int i = 0; i < vertices; i++) {
        graph->array[i].head = NULL;
        pthread_mutex_init(&graph->array[i].lock, NULL);
    }

    pthread_mutex_init(&graph->graph_lock, NULL);

    return graph;
}

void destroyGraph(Graph* graph) {
    for (int i = 0; i < graph->numVertices; i++) {
        Node* current = graph->array[i].head;
        while (current != NULL) {
            Node* temp = current;
            current = current->next;
            free(temp);
        }
        pthread_mutex_destroy(&graph->array[i].lock);
    }
    free(graph->array);
    pthread_mutex_destroy(&graph->graph_lock);
    free(graph);
}

Node* createNode(int vertex) {
    Node* newNode = (Node*)pmalloc(sizeof(Node));
    newNode->vertex = vertex;
    newNode->next = NULL;
    return newNode;
}

void addEdge(Graph* graph, int src, int dest) {
    pthread_mutex_lock(&graph->array[src].lock);

    Node* newNode = createNode(dest);
    newNode->next = graph->array[src].head;
    graph->array[src].head = newNode;

    pthread_mutex_unlock(&graph->array[src].lock);

    pthread_mutex_lock(&graph->array[dest].lock);

    newNode = createNode(src);
    newNode->next = graph->array[dest].head;
    graph->array[dest].head = newNode;

    pthread_mutex_unlock(&graph->array[dest].lock);
}

void removeEdge(Graph* graph, int src, int dest) {
    pthread_mutex_lock(&graph->array[src].lock);

    Node* temp = graph->array[src].head;
    Node* prev = NULL;
    while (temp != NULL && temp->vertex != dest) {
        prev = temp;
        temp = temp->next;
    }

    if (temp != NULL) {
        if (prev != NULL) {
            prev->next = temp->next;
        } else {
            graph->array[src].head = temp->next;
        }
        free(temp);
    }

    pthread_mutex_unlock(&graph->array[src].lock);

    // Remove edge from dest to src
    pthread_mutex_lock(&graph->array[dest].lock);

    temp = graph->array[dest].head;
    prev = NULL;
    while (temp != NULL && temp->vertex != src) {
        prev = temp;
        temp = temp->next;
    }

    if (temp != NULL) {
        if (prev != NULL) {
            prev->next = temp->next;
        } else {
            graph->array[dest].head = temp->next;
        }
        free(temp);
    }

    pthread_mutex_unlock(&graph->array[dest].lock);
}

int hasEdge(Graph* graph, int src, int dest) {
    pthread_mutex_lock(&graph->array[src].lock);

    Node* temp = graph->array[src].head;
    while (temp != NULL) {
        if (temp->vertex == dest) {
            pthread_mutex_unlock(&graph->array[src].lock);
            return 1; // Edge exists
        }
        temp = temp->next;
    }

    pthread_mutex_unlock(&graph->array[src].lock);
    return 0; 
}

void printGraph(Graph* graph) {
    for (int i = 0; i < graph->numVertices; i++) {
        pthread_mutex_lock(&graph->array[i].lock);

        Node* temp = graph->array[i].head;
        printf("Vertex %d:", i);
        while (temp) {
            printf(" -> %d", temp->vertex);
            temp = temp->next;
        }
        printf("\n");

        pthread_mutex_unlock(&graph->array[i].lock);
    }
}
