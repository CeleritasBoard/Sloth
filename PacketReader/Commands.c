//
// Created by andras on 2025.05.01..
//

#include "Commands.h"


#include "Commands.h"

//Global variables
unsigned numberOfHeaders = 0;
Header* headers = NULL;
Header* selectedHeaderp = NULL;
unsigned nextListID = 0;

#define DATALENGTH 33

void help(){
    printf("Commands:\n");
    printf(" h - help\n lsh - list headers\n sh [ID] - select header (ID is the list ID) \n"
        "ih [packet] - input header \n id - input data \n rd [packet] - raw decoding\n"
        "is [packet] - input selftest \n ie [packet] - input error \n e - exit\n");
}

//Header related functions-----------------------------------------

void printHeader(Header h){
    printf("ID: %d\n", h.ID);
    printf("IC: %d\n", h.IC);
    printf("T: %d\n", h.T);
    printf("t: %d\n", h.t);
    printf("res: %d\n", h.res);
    printf("min: %d\n", h.mr.min);
    printf("max: %d\n", h.mr.max);
    printf("Uref: %d\n", h.Uref);
    printf("headerID: %d\n", h.headerID);
    printf("CHS: %d\n", h.CHS);
}

void listHeaders(){
    for (unsigned i = 0; i < numberOfHeaders; i++)
    {
        printf("ID in the list: %d\n", (headers[i]).listID);
        printHeader(headers[i]);
        printf("---------------------------");
    }
}

void selectHeader(unsigned listID){

    selectedHeaderp = headers+listID;
    printf("Selected header: \n");
    printHeader(*selectedHeaderp);
}

unsigned getNum(char c1, char c2){
    unsigned out = 0;
    if(c1 <= '9' && c1 >= '0'){
        out += c1-'0';
    }
    else if (c1>='A' && c1 <= 'F')
    {
        out += c1-'A'+10;
    }
    else
    {
        printf("Invalid character");
    }
    out *= 16;
    if(c2 <= '9' && c2 >= '0'){
        out += c2-'0';
    }
    else if (c2>='A' && c2 <= 'F')
    {
        out += c2-'A'+10;
    }
    else
    {
        printf("Invalid character");
    }
    return out;
}

Header decodeHeader(char t[]){
    Header h;
    h.ID = getNum(t[0], t[1]);
    h.IC = getNum(t[2], t[3]);
    h.T = (getNum(t[4], t[5]) << 8) + getNum(t[6], t[7]);
    h.t = (getNum(t[8], t[9]) << 24) + (getNum(t[10], t[11]) << 16) + (getNum(t[12], t[13]) << 8) + getNum(t[14], t[15]);
    h.res = getNum(t[16], t[17]);
    h.mr.min = (getNum(t[18], t[19]) << 4) + (getNum(t[20], t[21]) >> 4);
    h.mr.max = (getNum(t[20], t[21])%16 << 8) + getNum(t[22], t[23]);
    h.Uref = (getNum(t[24], t[25]) << 8) + getNum(t[26], t[27]);
    h.headerID = getNum(t[28], t[29]);
    h.CHS = getNum(t[30], t[31]);
    h.listID = nextListID++;
    return h;
}

void inputHeader(char* data){
    unsigned length = strlen(data);
    if(length != DATALENGTH){
        printf("Invalid length\n");
        return;
    }
    Header h = decodeHeader(data);
    headers[h.listID] = h;
    printf("Header added to the list\n");
    printHeader(h);
    printf("Header listID: %d\n", h.listID);
}

//Data related functions-----------------------------------------

void inputData(){
    char data[DATALENGTH];
    printf("Selected header:\n");
    if (selectedHeaderp == NULL) {
        printf("No header selected\n");
        return;
    }
    printHeader(*selectedHeaderp);

    printf("You have to enter the %d data packets: " , selectedHeaderp->res==1 ? 1 : selectedHeaderp->res/8);
    for (unsigned i = 0; i < (selectedHeaderp->res==1 ? 1 : selectedHeaderp->res/8); i++)
    {
        printf("Enter the %d. packet: ", i);
        scanf("%s", data);
        if(strlen(data) % 4 != 0){
            printf("Invalid length");
            return;
        }
        printf("Data: ");
        for (unsigned i = 0; i < strlen(data); i+=4)
        {
            unsigned numBig = getNum(data[i], data[i+1]);
            numBig <<= 8;
            unsigned numLittle = getNum(data[i+2], data[i+3]);
            unsigned num = numBig + numLittle;
            printf(" %d", num);
        }
        printf("\n");

    }


}

//SelfTest related functions-----------------------------------------

selfTest decodeSelfTest(char t[]){
    selfTest st;
    st.ID = getNum(t[0], t[1]);
    st.T = (getNum(t[2], t[3]) << 8) + getNum(t[4], t[5]);
    st.Nerror = getNum(t[6], t[7]);
    st.t = (getNum(t[8], t[9]) << 24) + (getNum(t[10], t[11]) << 16) + (getNum(t[12], t[13]) << 8) + getNum(t[14], t[15]);
    st.KT1 = getNum(t[16], t[17]);
    st.KT2 = getNum(t[18], t[19]);
    st.LT = getNum(t[20], t[21]);
    st.Utest.min = (getNum(t[22], t[23]) << 4) + (getNum(t[24], t[25]) >> 4);
    st.Utest.max = (getNum(t[24], t[25])%16 << 8) + (getNum(t[26], t[27]));
    st.ST = getNum(t[28], t[29]);
    st.CHS = getNum(t[30], t[31]);
    return st;
}

void printSelfTest(selfTest st){
    printf("ID: %d\n", st.ID);
    printf("Temperature: %d\n", st.T);
    printf("Nerror: %d\n", st.Nerror);
    printf("time: %d\n", st.t);
    printf("Next measurement request1(KT1): %d\n", st.KT1);
    printf("Next measurement request2(KT2): %d\n", st.KT2);
    printf("LT: %d\n", st.LT);
    printf("Reference voltage(Utest1): %d\n", st.Utest.min);
    printf("avearge voltage(Utest2): %d\n", st.Utest.max);
    printf("SelfTest ID: %d\n", st.ST);
    printf("Checksum: %d\n", st.CHS);
}

void inputSelfTest(char* data){
    unsigned length = strlen(data);
    if(length != DATALENGTH){
        printf("Invalid length\n");
        return;
    }
    selfTest selftest = decodeSelfTest(data);
    printf("Decoded selftest: \n");
    printSelfTest(selftest);
}

//Error related functions-----------------------------------------

Error decodeError(char t[]){
    Error e;
    e.ID = getNum(t[0], t[1]);
    e.errorCode = getNum(t[26], t[27]);
    e.errorID = getNum(t[28], t[29]);
    e.CHS = getNum(t[30], t[31]);
    return e;
}

void printError(Error e){
    printf("ID: %d\n", e.ID);
    switch (e.errorCode)
    {
    case 0xFD:
        printf("Timeout error\n");
        break;
    case 0xF7:
        printf("Corrupted packet\n");
        break;
    case 0xFB:
        printf("Interrupt error\n");
        break;
    default:
        printf("Unknown error\n");
        break;
    }
    printf("Error ID: %d\n", e.errorID);
    printf("Checksum: %d\n", e.CHS);
}

void inputError(char* data){
    unsigned length = strlen(data);
    if(length != DATALENGTH){
        printf("Invalid length");
        return;
    }
    Error selftest = decodeError(data);
    printf("Decoded error: \n");
}

void rawDecoding(char* data){
    printf("Code: ");
    for (int i = 0; i < strlen(data); i+=2)
    {
        unsigned num = getNum(data[i], data[i+1]);
        printf("%d ", num);
    }

}

void exitCommandReader(){
    free(headers);
    exit(0);
}