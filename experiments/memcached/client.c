#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <stdint.h>
#include <netinet/in.h>

#define SERVER "127.0.0.1"
#define PORT 11211
#define BUFFER_SIZE 1024
#define GET_OPCODE 0x00

// Memcached binary protocol request header structure
typedef struct {
    uint8_t magic;
    uint8_t opcode;
    uint16_t key_length;
    uint8_t extras_length;
    uint8_t data_type;
    uint16_t vbucket_id;
    uint32_t total_body_length;
    uint32_t opaque;
    uint64_t cas;
} memcached_binary_request_header_t;

typedef struct {
    uint8_t magic;
    uint8_t opcode;
    uint16_t key_length;
    uint8_t extras_length;
    uint8_t data_type;
    uint16_t status;
    uint32_t total_body_length;
    uint32_t opaque;
    uint64_t cas;
} memcached_binary_response_header_t;

// Define htonll and ntohll for 64-bit integers
#if __BYTE_ORDER == __LITTLE_ENDIAN
    uint64_t htonll(uint64_t value) {
        return (((uint64_t)htonl(value & 0xFFFFFFFFULL)) << 32) | htonl(value >> 32);
    }

    uint64_t ntohll(uint64_t value) {
        return (((uint64_t)ntohl(value & 0xFFFFFFFFULL)) << 32) | ntohl(value >> 32);
    }
#else
    uint64_t htonll(uint64_t value) {
        return value;
    }

    uint64_t ntohll(uint64_t value) {
        return value;
    }
#endif

// Function to retrieve a value by key from Memcached using binary protocol
void get_key_value(int sockfd, const char *key) {
    uint16_t key_length = strlen(key);
    uint32_t total_body_length = key_length;

    char buffer[BUFFER_SIZE];
    memset(buffer, 0, sizeof(buffer));

    // Build the binary request header for GET command
    buffer[0] = 0x80;              // Magic byte for request
    buffer[1] = GET_OPCODE;         // Opcode for GET command (0x00)
    buffer[2] = (key_length >> 8) & 0xFF; // Key length high byte
    buffer[3] = key_length & 0xFF;  // Key length low byte
    buffer[4] = 0;                  // Extras length (no extras for GET)
    buffer[5] = 0;                  // Data type (reserved)
    buffer[6] = 0;                  // VBucket (reserved for 0)
    buffer[7] = 0;                  // VBucket (reserved for 0)
    
    // Total body length (key length)
    buffer[8] = (total_body_length >> 24) & 0xFF;
    buffer[9] = (total_body_length >> 16) & 0xFF;
    buffer[10] = (total_body_length >> 8) & 0xFF;
    buffer[11] = total_body_length & 0xFF;

    buffer[12] = 0; // Opaque (client-specific, set to 0)
    buffer[13] = 0;
    buffer[14] = 0;
    buffer[15] = 0;

    // CAS (set to 0)
    buffer[16] = 0;
    buffer[17] = 0;
    buffer[18] = 0;
    buffer[19] = 0;
    buffer[20] = 0;
    buffer[21] = 0;
    buffer[22] = 0;
    buffer[23] = 0;

    // Copy the key into the buffer
    memcpy(buffer + 24, key, key_length);

    // Send the GET request
    if (send(sockfd, buffer, 24 + key_length, 0) < 0) {
        error("Send failed");
    }

    // Receive the response
    memset(buffer, 0, sizeof(buffer));
    if (recv(sockfd, buffer, sizeof(buffer), 0) < 0) {
        error("Receive failed");
    }

    // Parse the response
    uint8_t magic = buffer[0];
    uint8_t opcode = buffer[1];
    uint16_t key_length_response = ntohs(*(uint16_t *)(buffer + 2));
    uint8_t extras_length = buffer[4];
    uint32_t body_length = ntohl(*(uint32_t *)(buffer + 8));
    uint16_t status = ntohs(*(uint16_t *)(buffer + 6)); // Status field in the response

    if (magic == 0x81 && opcode == GET_OPCODE) { // 0x81 is the magic byte for a response
        if (status == 0x0000) { // 0x0000 means NO ERROR (successful response)
            printf("GET succeeded.\n");

            // Extract the extras if there are any (for GET, there's usually none)
            uint32_t value_length = body_length - extras_length - key_length_response;
            const char *value = buffer + 24 + extras_length; // The value starts after the extras and key

            // Print the value
            printf("Key: %s\n", key);
            printf("Value: %.*s\n", value_length, value);
        } else {
            printf("Error retrieving key: %u\n", status);
        }
    } else {
        printf("Unexpected response.\n");
    }
}

void read_server_response(int sockfd) {
    char buffer[BUFFER_SIZE];
    ssize_t n = recv(sockfd, buffer, sizeof(buffer), 0);
    if (n < 0) {
        perror("Receive failed");
        return;
    }

    // Check if we received a binary protocol response
    uint8_t magic = buffer[0];
    uint8_t opcode = buffer[1];
    uint16_t status = ntohs(*(uint16_t *)(buffer + 6));
    uint32_t body_length = ntohl(*(uint32_t *)(buffer + 8));

    if (magic != 0x81) {
        printf("Invalid response from server\n");
        return;
    }

    if (status != 0x0000) {
        printf("Server error: %u\n", status);
        return;
    }

    if (opcode == 0x05) { 
        if (body_length == 8) {
            uint64_t new_value = ntohll(*(uint64_t *)(buffer + 24)); 
            printf("New value after INCR: %llu\n", (unsigned long long)new_value);
        } else {
            printf("Unexpected body length for INCR: %u\n", body_length);
        }
    } else if (opcode == 0x0E) { 
        if (body_length == 0) {
            printf("APPEND command was successful.\n");
        } else {
            printf("Unexpected body length for APPEND: %u\n", body_length);
        }
    } else if (opcode == 0x0F) { 
        if (body_length == 0) {
            printf("PREPEND command was successful.\n");
        } else {
            printf("Unexpected body length for PREPEND: %u\n", body_length);
        }
    } else {
    printf("Unexpected opcode: %u\n", opcode);
    }

}

void error(const char *msg) {
    perror(msg);
    exit(1);
}

void send_binary_set_command(int sockfd, const char *key, const char *value) {
    memcached_binary_request_header_t header;
    uint32_t flags = 0;  // Flags for the SET command
    uint32_t expiration = 10;  // Expiration (0 means no expiration)
    
    uint16_t key_length = strlen(key);
    uint32_t value_length = strlen(value);
    uint32_t extras_length = 8;  // Extras length (4 bytes for flags, 4 bytes for expiration)
    uint32_t total_body_length = extras_length + key_length + value_length;

    // Fill the header
    header.magic = 0x80;  // Request magic byte
    header.opcode = 0x01;  // Opcode for the SET command
    header.key_length = htons(key_length);
    header.extras_length = extras_length;
    header.data_type = 0x00;  // Reserved, always 0
    header.vbucket_id = 0x0000;  // Always 0 for Memcached
    header.total_body_length = htonl(total_body_length);
    header.opaque = 0x00000000;  // Any unique identifier
    header.cas = 0x0000000000000000;  // CAS value (0 if not used)

    // Prepare buffer for the entire message
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);

    // Copy the header to the buffer
    memcpy(buffer, &header, sizeof(memcached_binary_request_header_t));

    // Copy the extras (flags and expiration)
    uint32_t network_flags = htonl(flags);
    uint32_t network_expiration = htonl(expiration);
    memcpy(buffer + sizeof(memcached_binary_request_header_t), &network_flags, 4);
    memcpy(buffer + sizeof(memcached_binary_request_header_t) + 4, &network_expiration, 4);

    // Copy the key and value
    memcpy(buffer + sizeof(memcached_binary_request_header_t) + extras_length, key, key_length);
    memcpy(buffer + sizeof(memcached_binary_request_header_t) + extras_length + key_length, value, value_length);

    // Send the entire message
    if (send(sockfd, buffer, sizeof(memcached_binary_request_header_t) + total_body_length, 0) < 0) {
        error("Send failed");
    }

    receive_binary_response(sockfd);
}

void receive_binary_response(int sockfd) {
    memcached_binary_response_header_t response_header;
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);

    // Receive the response header (24 bytes)
    if (recv(sockfd, &response_header, sizeof(memcached_binary_response_header_t), 0) < 0) {
        error("Receive header failed");
    }

    // Convert values from network byte order to host byte order
    response_header.status = ntohs(response_header.status);
    response_header.total_body_length = ntohl(response_header.total_body_length);

    // Check the status code (0x0000 is success)
    if (response_header.status == 0x0000) {
        printf("SET command succeeded!\n");
    } else {
        printf("SET command failed with status: 0x%04x\n", response_header.status);
    }

    // If there is a body, read it
    if (response_header.total_body_length > 0) {
        if (recv(sockfd, buffer, response_header.total_body_length, 0) < 0) {
            error("Receive body failed");
        }
        printf("Response body: %s\n", buffer);
    }
}

// Function to write data objects
void *write_data(void *arg, int sockfd, struct sockaddr_in server_addr) {
    int thread_id = *((int *)arg);
    // int sockfd;
    // struct sockaddr_in server_addr;

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

    for (int i = 0; i < 5; ++i) {
        char key[BUFFER_SIZE];
        char value[BUFFER_SIZE];
        snprintf(key, sizeof(key), "key%d", i+1);
        snprintf(value, sizeof(value), "%d", i+1);
	    printf("%s, %s\n", key, value);
        send_binary_set_command(sockfd, key, value);
        get_key_value(sockfd, key);
        send_binary_incr_command(sockfd, key, 5, value, 0);
        send_binary_command(sockfd, key, "10", 1); // 1 for APPEND
        send_binary_command(sockfd, key, "12", 0); // 0 for PREPEND

        
    }

}

void send_binary_command(int sockfd, const char *key, const char *value, int is_append) {
    memcached_binary_request_header_t header;

    uint16_t key_length = strlen(key);
    uint32_t value_length = strlen(value);
    uint32_t total_body_length = key_length + value_length;

    // Fill the header
    header.magic = 0x80;  // Request magic byte (0x80 for request)
    header.key_length = htons(key_length);
    header.extras_length = 0;  // No extras
    header.data_type = 0x00;  // Reserved, always 0
    header.vbucket_id = 0x0000;  // Always 0 for Memcached
    header.total_body_length = htonl(total_body_length);
    header.opaque = 0x00000000;  // Any unique identifier
    header.cas = 0x0000000000000000;  // CAS value (0 if not used)

    // Set the opcode based on the command type
    header.opcode = is_append ? 0x0E : 0x0F;  // 0x0E for APPEND, 0x0F for PREPEND

    // Prepare the buffer for the entire message
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);

    // Copy the header to the buffer
    memcpy(buffer, &header, sizeof(memcached_binary_request_header_t));

    // Copy the key to the buffer
    memcpy(buffer + sizeof(memcached_binary_request_header_t), key, key_length);
    
    // Copy the value to the buffer
    memcpy(buffer + sizeof(memcached_binary_request_header_t) + key_length, value, value_length);

    // Send the command
    if (send(sockfd, buffer, sizeof(memcached_binary_request_header_t) + total_body_length, 0) < 0) {
        error("Send failed");
    }

    memset(buffer, 0, BUFFER_SIZE);
    read_server_response(sockfd);
}

void send_binary_incr_command(int sockfd, const char *key, uint64_t delta, uint64_t initial_value, uint32_t expiration) {
    memcached_binary_request_header_t header;
    uint32_t flags = 0;  

    uint16_t key_length = strlen(key);
    uint32_t extras_length = 20; 
    uint32_t total_body_length = extras_length + key_length;

    header.magic = 0x80;  
    header.opcode = 0x05; 
    header.key_length = htons(key_length);
    header.extras_length = extras_length;
    header.data_type = 0x00; 
    header.vbucket_id = 0x0000;  
    header.total_body_length = htonl(total_body_length);
    header.opaque = 0x00000000;  
    header.cas = 0x0000000000000000;  

    char buffer[BUFFER_SIZE];
    memset(buffer, 0, BUFFER_SIZE);

    memcpy(buffer, &header, sizeof(memcached_binary_request_header_t));

    uint64_t network_delta = htonll(delta);         
    uint64_t network_initial_value = htonll(initial_value); 
    uint32_t network_expiration = htonl(expiration);       
    memcpy(buffer + sizeof(memcached_binary_request_header_t), &network_delta, 8);
    memcpy(buffer + sizeof(memcached_binary_request_header_t) + 8, &network_initial_value, 8);
    memcpy(buffer + sizeof(memcached_binary_request_header_t) + 16, &network_expiration, 4);

    memcpy(buffer + sizeof(memcached_binary_request_header_t) + extras_length, key, key_length);

    if (send(sockfd, buffer, sizeof(memcached_binary_request_header_t) + total_body_length, 0) < 0) {
        error("Send failed");
    }

    memset(buffer, 0, BUFFER_SIZE);
	read_server_response(sockfd);
}

int main() {
    int sockfd;
    struct sockaddr_in server_addr;

    if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        error("Socket creation failed");
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    if (inet_pton(AF_INET, SERVER, &server_addr.sin_addr) <= 0) {
        error("Invalid address");
    }

    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        error("Connection to server failed");
    }

    int NUM_THREADS = 2;
    pthread_t threads[NUM_THREADS];
    int thread_ids[NUM_THREADS];

    // Create two threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        thread_ids[i] = i + 1;
        if (pthread_create(&threads[i], NULL, write_data, &thread_ids[i], sockfd, server_addr) != 0) {
            error("Failed to create thread");
        }
    }

    // Join the threads
    for (int i = 0; i < NUM_THREADS; ++i) {
        pthread_join(threads[i], NULL);
    }

    // send_binary_incr_command(sockfd, "key1", 5, 2, 0);
    // send_binary_command(sockfd, "key1", 10, 1); // 1 for APPEND
    // send_binary_command(sockfd, "key1", 12, 0); // 0 for PREPEND

    close(sockfd);

    return 0;
}
