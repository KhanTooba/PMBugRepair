#ifndef GRAPH_H
#define GRAPH_H
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include "pm.h"

// Structure to represent a node in the adjacency list
typedef struct Node {
    int vertex;
    struct Node* next;
} Node;

// Structure to represent the adjacency list
typedef struct {
    Node* head;
    pthread_mutex_t lock; // Lock for each adjacency list
} AdjList;

// Structure to represent a graph
typedef struct {
    int numVertices;
    AdjList* array;
    pthread_mutex_t graph_lock; // Global lock for the graph
} Graph;

// Function prototypes
Graph* createGraph(int vertices);
void destroyGraph(Graph* graph);
void addEdge(Graph* graph, int src, int dest);
void removeEdge(Graph* graph, int src, int dest);
void printGraph(Graph* graph);
int hasEdge(Graph* graph, int src, int dest);

#endif // GRAPH_H

// Function to create a graph
Graph* createGraph(int vertices) {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    graph->numVertices = vertices;
    graph->array = (AdjList*)malloc(vertices * sizeof(AdjList));

    // Initialize each adjacency list and mutexes
    for (int i = 0; i < vertices; i++) {
        graph->array[i].head = NULL;
        pthread_mutex_init(&graph->array[i].lock, NULL);
    }

    pthread_mutex_init(&graph->graph_lock, NULL);

    return graph;
}

// Function to destroy a graph
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

// Function to create a new node
Node* createNode(int vertex) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->vertex = vertex;
    newNode->next = NULL;
    return newNode;
}

// Function to add an edge to the graph
void addEdge(Graph* graph, int src, int dest) {
    pthread_mutex_lock(&graph->array[src].lock);

    // Add edge from src to dest
    Node* newNode = createNode(dest);
    newNode->next = graph->array[src].head;
    graph->array[src].head = newNode;

    pthread_mutex_unlock(&graph->array[src].lock);

    // Since the graph is undirected, add an edge from dest to src
    pthread_mutex_lock(&graph->array[dest].lock);

    newNode = createNode(src);
    newNode->next = graph->array[dest].head;
    graph->array[dest].head = newNode;

    pthread_mutex_unlock(&graph->array[dest].lock);
}

// Function to remove an edge from the graph
void removeEdge(Graph* graph, int src, int dest) {
    pthread_mutex_lock(&graph->array[src].lock);

    // Remove edge from src to dest
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

// Function to check if there is an edge between two vertices
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
    return 0; // Edge does not exist
}

// Function to print the graph
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
