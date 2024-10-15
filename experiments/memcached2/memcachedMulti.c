#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>

#define SERVER "127.0.0.1"
#define PORT 11211
#define BUFFER_SIZE 1024
#define NUM_THREADS 2
#define DATA_PER_THREAD 5

void error(const char *msg) {
    perror(msg);
    exit(1);
}

// Function to write data objects
void *write_data(void *arg) {
    int thread_id = *((int *)arg);
    int sockfd;
    struct sockaddr_in server_addr;
    char buffer[BUFFER_SIZE];

    // Create a socket
    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        error("Socket creation failed");
    }

    // Set server address and port
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, SERVER, &server_addr.sin_addr) <= 0) {
        error("Invalid address");
    }

    // Connect to the server
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        error("Connection to server failed");
    }
	int val = 150;
    // Write 5 data objects per thread
    for (int i = val; i < val+DATA_PER_THREAD; ++i) {
        char set_command[BUFFER_SIZE];
        char value[BUFFER_SIZE];
        snprintf(value, sizeof(value), "value%d", i+10);  // The data to store (e.g., "value0", "value1", ...)
        size_t value_len = strlen(value);

        // Format the set command
        snprintf(set_command, sizeof(set_command),
                 "set thread%d_key%d 0 100 %zu\r\n%s\r\n", // Correctly formatting the command
                 thread_id, i+10, value_len, value);

        // Print the set command being sent
        // printf("Thread %d - Sending SET command: %s", thread_id, set_command);

        // Send a SET command
        if (send(sockfd, set_command, strlen(set_command), 0) < 0) {
            error("Send failed");
        }

        // Receive the response
        memset(buffer, 0, BUFFER_SIZE);
        if (recv(sockfd, buffer, BUFFER_SIZE - 1, 0) < 0) {
            error("Receive failed");
        }
        printf("Thread %d - Server response: %s\n", thread_id, buffer);
    }

    // Close the socket
    close(sockfd);
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    int thread_ids[NUM_THREADS];

    // Create two threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        thread_ids[i] = i + 1;
        if (pthread_create(&threads[i], NULL, write_data, &thread_ids[i]) != 0) {
            error("Failed to create thread");
        }
    }

    // Join the threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}
