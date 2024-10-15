#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define SERVER "127.0.0.1"
#define PORT 11211
#define BUFFER_SIZE 1024

void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main() {
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

    // Send a SET command
    const char *set_command = "set tooba'sKey 1 100 4\r\n1234\r\n";
    if (send(sockfd, set_command, strlen(set_command), 0) < 0) {
        error("Send failed");
    }

    // Receive the response
    memset(buffer, 0, BUFFER_SIZE);
    if (recv(sockfd, buffer, BUFFER_SIZE - 1, 0) < 0) {
        error("Receive failed");
    }
    printf("Server response: %s\n", buffer);

    // Send a GET command
    const char *get_command = "get tooba'sKey\r\n";
    if (send(sockfd, get_command, strlen(get_command), 0) < 0) {
        error("Send failed");
    }

    // Receive the response
    memset(buffer, 0, BUFFER_SIZE);
    if (recv(sockfd, buffer, BUFFER_SIZE - 1, 0) < 0) {
        error("Receive failed");
    }
    printf("Server response: %s\n", buffer);

    // Close the socket
    close(sockfd);

    return 0;
}
