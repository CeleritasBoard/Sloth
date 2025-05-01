//
// Created by andras on 2025.05.01..
//

#ifndef COMMANDS_H
#define COMMANDS_H


#include <stdio.h>
#include <string.h>
#include <stdlib.h>

//Structures
typedef struct measurementRange{
    unsigned min: 12;
    unsigned max: 12;
}measurementRange;

typedef struct Header
{
    __uint8_t listID;
    __uint8_t ID;
    __uint8_t IC;
    __uint16_t T;
    __uint32_t t;
    __uint8_t res;
    measurementRange mr;
    __uint16_t Uref;
    __uint8_t headerID;
    __uint8_t CHS;
} Header;

typedef struct selfTest
{
    __uint8_t ID;
    __uint16_t T;
    __uint8_t Nerror;
    __uint32_t t;
    __uint8_t KT1;
    __uint8_t KT2;
    __uint8_t LT;
    measurementRange Utest;
    __uint8_t ST;
    __uint8_t CHS;
} selfTest;

typedef struct Error
{
    __uint8_t ID;
    __uint8_t errorCode;
    __uint8_t errorID;
    __uint8_t CHS;
} Error;


//Global variables
extern unsigned numberOfHeaders;
extern Header* headers;
extern Header* selectedHeaderp;
extern unsigned nextListID;

//Function prototypes
void help();
void printHeader(Header h);
void listHeaders();
void selectHeader(unsigned uargument);
Header decodeHeader(char t[]);
void inputHeader(char* data);
void inputData();
void inputSelfTest(char* data);
void inputError(char* data);
void rawDecoding(char* data);
void exitCommandReader();



#endif //COMMANDS_H
