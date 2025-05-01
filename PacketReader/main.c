
#include<stdio.h>
#include<string.h>
#include<stdlib.h>
#include"Commands.h"
#include <unistd.h>



void identifyCommand(char com[]){
    char* command = com;
    char* argument;
    int uargument;
    //strcpy(command, com);
    char* tok = strtok(command, " ");
    if(!strcmp(command, "h\n")){
        help();
    }
    else if (!strcmp(command, "lsh\n"))
    {
        listHeaders();
    }
    else if (!strcmp(tok, "sh"))
    {
        argument = strtok(NULL, " ");
        sscanf(argument, "%d", &uargument);
        selectHeader(uargument);
    }
    else if (!strcmp(tok, "ih")) {
        tok = strtok(NULL, " ");
        inputHeader(tok);
    }
    else if (!strcmp(tok, "id"))
    {
        inputData();
    }
    else if (!strcmp(tok, "is"))
    {
        tok = strtok(NULL, " ");
        inputSelfTest(tok);
    }
    else if (!strcmp(tok, "ie"))
    {
        tok = strtok(NULL, " ");
        inputError(tok);
    }
    else if(!strcmp(tok, "rd")){
        tok = strtok(NULL, " ");
        rawDecoding(tok);
    }
    else if(!strcmp(command, "e\n")){
        exitCommandReader();
    }
    else
    {
        printf("Invalid command\n");
    }
    //free(command);
    //free(argument);
    //free(commandType);
    
}

//How to run:
//gcc Commands.c Reader.c -o program


int main(){
    //Variables
    size_t COMMANDLENGTH = 100;
    char* command;
    
    printf("First you have to enter the number of headers. Number of headers: ");
    scanf("%d", &numberOfHeaders);
    headers = (Header*)(malloc(numberOfHeaders*sizeof(Header)));
    help();
    
    
    while (1)
    {
        printf("Enter a command: ");
        sleep(1);
        getline(&command, &COMMANDLENGTH, stdin);
        printf("\nCommand: %s\n", command);
        identifyCommand(command);

    }
    
    return 0;
}


//0123456789ABCDEF0123456789ABCDEF