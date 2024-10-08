import streamlit as st

# Client C Code
client_code = """
#include <stdio.h>
#include <stdlib.h> // For exit() and atoi()
#include <string.h> // For strlen() and memset()
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h> // For read() and write()
#define MAX_INPUT_SIZE 256

int main(int argc, char *argv[]) {
    int sockfd, portnum, n;
    struct sockaddr_in server_addr;
    char inputbuf[MAX_INPUT_SIZE];

    if (argc < 3) {
        fprintf(stderr, "usage %s <server-ip-addr> <server-port>\n", argv[0]);
        exit(0);
    }

    portnum = atoi(argv[2]);

    /* Create client socket */
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        fprintf(stderr, "ERROR opening socket\n");
        exit(1);
    }

    /* Fill in server address */
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    if (!inet_aton(argv[1], &server_addr.sin_addr)) {
        fprintf(stderr, "ERROR invalid server IP address\n");
        exit(1);
    }
    server_addr.sin_port = htons(portnum);

    /* Connect to server */
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        fprintf(stderr, "ERROR connecting\n");
        exit(1);
    }
    printf("Connected to server\n");

    do {
        /* Ask user for message to send to server */
        printf("Please enter the message to the server: ");
        memset(inputbuf, 0, MAX_INPUT_SIZE);
        fgets(inputbuf, MAX_INPUT_SIZE - 1, stdin);

        /* Write to server */
        n = write(sockfd, inputbuf, strlen(inputbuf));
        if (n < 0) {
            fprintf(stderr, "ERROR writing to socket\n");
            exit(1);
        }

        /* Read reply */
        memset(inputbuf, 0, MAX_INPUT_SIZE);
        n = read(sockfd, inputbuf, (MAX_INPUT_SIZE - 1));
        if (n < 0) {
            fprintf(stderr, "ERROR reading from socket\n");
            exit(1);
        }
        printf("Server replied: %s\n", inputbuf);

        /* Check that reply is either OK or Goodbye */
        if (!((inputbuf[0] == 'G' && inputbuf[1] == 'o' && inputbuf[2] == 'o' &&
               inputbuf[3] == 'd' && inputbuf[4] == 'b' && inputbuf[5] == 'y' && inputbuf[6] == 'e') ||
              (inputbuf[0] == 'O' && inputbuf[1] == 'K'))) {
            fprintf(stderr, "ERROR wrong reply from server\n");
            exit(1);
        }
    } while (!(inputbuf[0] == 'G' && inputbuf[1] == 'o' && inputbuf[2] == 'o' &&
               inputbuf[3] == 'd' && inputbuf[4] == 'b' && inputbuf[5] == 'y' && inputbuf[6] == 'e'));

    return 0;
}
"""

# Server C Code
server_code = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#define MAX_INPUT_SIZE 256

void handleError(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    int sockfd, newsockfd, portnum, n;
    socklen_t clilen;
    char buffer[MAX_INPUT_SIZE];
    struct sockaddr_in server_addr, client_addr;

    if (argc < 2) {
        fprintf(stderr, "ERROR, no port provided\n");
        exit(1);
    }

    /* Create socket */
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
        handleError("ERROR opening socket");

    /* Prepare server address */
    bzero((char *)&server_addr, sizeof(server_addr));
    portnum = atoi(argv[1]);
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(portnum);

    /* Bind the socket to the server address */
    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
        handleError("ERROR on binding");

    /* Start listening for incoming connections */
    listen(sockfd, 5);
    clilen = sizeof(client_addr);

    /* Accept a connection from a client */
    newsockfd = accept(sockfd, (struct sockaddr *)&client_addr, &clilen);
    if (newsockfd < 0)
        handleError("ERROR on accept");

    printf("Client connected\n");

    while (1) {
        /* Clear the buffer */
        bzero(buffer, MAX_INPUT_SIZE);

        /* Read the client's message */
        n = read(newsockfd, buffer, MAX_INPUT_SIZE - 1);
        if (n < 0)
            handleError("ERROR reading from socket");
        printf("Client message: %s\n", buffer);

        /* Check the message and send appropriate responses */
        if (strncmp("Bye", buffer, 3) == 0) {
            n = write(newsockfd, "Goodbye", 7);
            if (n < 0)
                handleError("ERROR writing to socket");
            break; // Exit the loop when "Bye" is received
        } else if (strncmp("Hello", buffer, 5) == 0 || strncmp("Hi", buffer, 2) == 0) {
            n = write(newsockfd, "OK", 2);
            if (n < 0)
                handleError("ERROR writing to socket");
        } else {
            n = write(newsockfd, "OK", 2); // Even for other messages, respond with "OK"
            if (n < 0)
                handleError("ERROR writing to socket");
        }
    }

    close(newsockfd);
    close(sockfd);
    return 0;
}
"""


#Server code for calculator:-
#    A simple server in the internet domain using TCP
#    The port number is passed as an argument 
#    This version runs forever, forking off a separate 
#    process for each connection
#    gcc server2.c -o server2


       
cal_server = """
#include <stdio.h>
#include <stdlib.h>        // Include for exit() and atoi()
#include <string.h>        // Include for bzero()
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>        // Include for fork(), close(), read(), write()

void dostuff(int); /* function prototype */
void error(char *msg)
{
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[])
{
     int sockfd, newsockfd, portno, clilen, pid;
     struct sockaddr_in serv_addr, cli_addr;

     if (argc < 2) {
         fprintf(stderr,"ERROR, no port provided\n");
         exit(1);
     }
     sockfd = socket(AF_INET, SOCK_STREAM, 0);
     if (sockfd < 0) 
        error("ERROR opening socket");
     bzero((char *) &serv_addr, sizeof(serv_addr));
     portno = atoi(argv[1]);
     serv_addr.sin_family = AF_INET;
     serv_addr.sin_addr.s_addr = INADDR_ANY;
     serv_addr.sin_port = htons(portno);
     if (bind(sockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) 
              error("ERROR on binding");
     listen(sockfd, 5);
     clilen = sizeof(cli_addr);
     while (1) {
         newsockfd = accept(sockfd, (struct sockaddr *) &cli_addr, (socklen_t *)&clilen);
         if (newsockfd < 0) 
             error("ERROR on accept");
         pid = fork();
         if (pid < 0)
             error("ERROR on fork");
         if (pid == 0)  {
             close(sockfd);
             dostuff(newsockfd);
             exit(0);
         }
         else close(newsockfd);
     } /* end of while */
     return 0; /* we never get here */
}

/******** DOSTUFF() *********************
 There is a separate instance of this function 
 for each connection.  It handles all communication
 once a connnection has been established.
 *****************************************/
void dostuff (int sock)
{
   int n;
   char buffer[256];
      
   bzero(buffer, 256);
   n = read(sock, buffer, 255);
   int i = 0;
   int a = 0;
   int b = 0;
   while(buffer[i]>=48 && buffer[i]<=57)
   {
    a = a*10+(buffer[i]-48);
    i++;
   }
   int d = i;
   i++;
   while(buffer[i]>=48 && buffer[i]<=57)
   {
    b = b*10+(buffer[i]-48);
    i++;
   }
   int c ;
   if(buffer[d]=='+')
   {
    c = a+b;
   }
   else if (buffer[d]=='-')
   {
    c = a-b;
   }
   else if(buffer[d]=='*')
   {
    c = a*b;
   }
   else if (buffer[d]=='/')
   {
    c = (float)a/b;
   }
   char result[256];
   snprintf(result, sizeof(result), "Result: %d", (int)c);
   if (n < 0) error("ERROR reading from socket");
   printf("Result is : %d\n", c);
   n = write(sock, result, strlen(result));
   if (n < 0) error("ERROR writing to socket");
}
"""

# Streamlit interface to display the code
st.title("C Socket Client-Server Code")

# Display Client Code
st.subheader("Client Code")
st.code(client_code, language='c')

# Display Server Code
st.subheader("Server Code")
st.code(server_code, language='c')

st.subheader("Server calculation Code")
st.code(cal_server, language='c')
