import serial
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import csv
import threading
import time



Data_buffer = []
packet_info = []
Command = []

clear = lambda: os.system('cls')


def fetch_packet():
    s = []
    ser = serial.Serial('COM3', 115200, timeout=1)
    ser.write(b'a51')
    print(ser.readline())      #discard this information
    temp = []
    ser.write(b'r')
    print(ser.readline())     #discard this information
    time.sleep(1/10)
    temp = ser.readline()
    temp = temp[1:33].decode("utf-8")
    for k in range(16):
        value = int(temp[2*k:2*k+2], 16)
        s.append(value)
    print(ser.readline())      #discard this information
    print(s)
    ser.close()
    return s

def spectrum_values(spectrum_packet:list):
    values = []
    for k in range(16):
        value = 16 * spectrum_packet[2*k] + spectrum_packet[2*k+1]
        values.append(value)

def process_data():
    global packet_info
    global Data_buffer
    packet_info = []
    for k in range(len(Data_buffer)):
        if Data_buffer[k][0] != 0:
            if Data_buffer[k] == [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]:
                packet_info.append('Empty flash dump')
                continue
            if Data_buffer[k][14] == 255:
                packet_info.append('Header')
                continue
            if Data_buffer[k][14] == 254:
                packet_info.append('Selftest')
                continue
            if Data_buffer[k][14] == 213:
                if Data_buffer[k][13] == 240:
                    packet_info.append('TERMINATED ERROR')
                    continue
                if Data_buffer[k][13] == 253:
                    packet_info.append('TIMEOUT ERROR')
                    continue
                if Data_buffer[k][13] == 247:
                    packet_info.append('CORRUPTED ERROR')
                    continue
                if Data_buffer[k][13] == 251:
                    packet_info.append('MEASUREMENT ERROR')
                    continue
            else:
                packet_info.append('Spectrum')
        else:
            if Data_buffer[k] == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
                packet_info.append('Startup packet')
            else:
                if Data_buffer[k][0:8] == [0, 170, 0, 0, 0, 0, 0, 0]:
                    packet_info.append('Geiger count')
                else:
                    packet_info.append('Spectrum')

def read_data():
    end = 0
    while end == 0:
        read = fetch_packet()
        if((read[0] != 0) and (read[14] == 255)):
            Data_buffer.append(read)
            if read == [255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]:
                continue
            packetcount = read[8]
            for i in range(packetcount):
                read_sub = fetch_packet()
                Data_buffer.append(read_sub)
            continue
        if(read == [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]):
            print("All zeros, no header detected: terminated read")
            end = 1
            continue
        Data_buffer.append(read)
    process_data()

def print_data():
    process_data()
    if Data_buffer == []:
        print("No collected data")
    for k in range(len(Data_buffer)):
        print(Data_buffer[k], packet_info[k])

def commander():

    def checksum(the_bytes:list):
        checksum = 0
        for i in range(len(the_bytes)):
            checksum += bin(the_bytes[i]).count('1')
        return checksum

    global Command
    print("Select a command:")
    print("[0]. Set duration")
    print("[1]. Set scale")
    print("[2]. Request measurement")
    print("[3]. Request selftest")
    print("[4]. Reset")
    print("[5]. Restart")
    print("[6]. Previous commands")
    print("Any other to cancle")
    command_type = input("Choose command [0-6]:")
    if command_type == '4':
        ID = 0
        if (ID > 255) or (ID < 1):
            ID = input("Command Id [1-255]:")
        the_data = 'w0F' + str(ID)
        the_bytes = [0x0F, int(ID), 0x00, 0x00, 0x00, 0x00, 0x00]
        the_bytes.append(checksum(the_bytes))
        Command.append(the_bytes)
        converted = 'w'
        for i in range(len(the_bytes)):
            converted += str(the_bytes[i])
        converted += '\r\n'
        converted = bytes(converted, "utf-8")
        print(the_bytes)
        print(converted)
        ser = serial.Serial('COM3', 115200, timeout=0.01)
        ser.write(the_bytes)
        print(ser.read())
        print(ser.read())
        ser.close()

def write_loop():
    global end
    global wait
    wait = 0
    end = 0
    global ser
    ser = serial.Serial('COM3', 115200, timeout=0.01)

    def pollI2C():
        global end
        global wait
        global ser
        while end == 0:
            if wait == 0:
                react = ser.readline()
                if((react != b'') and (react != b'\r\n')):
                    print(react)
        return

    def user_input():
        global end
        global wait
        global ser


        while end == 0:
            INPUT = input()
            wait = 1
            if(INPUT == "EXIT"):
                end = 1
                return
            time.sleep(0.1)
            INPUT = INPUT.encode("utf-8")
            ser.write(INPUT)
            wait = 0
        return
    
    print("Input \" EXIT \" to exit the loop")

    t1 = threading.Thread(target=pollI2C, args=())
    t2 = threading.Thread(target=user_input, args=())

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    ser.close()


def Display():
    print("Spectrums are found by looking for Header packets")
    positions = []
    pos_types = []
    IDs = []
    for i in range(len(packet_info)):
        if packet_info[i] == 'Header' or packet_info[i] == 'Selftest':
            positions.append(i)
    for i in range(len(positions)):
        pos_types.append(packet_info[positions[i]])
        IDs.append(Data_buffer[positions[i]][0])
    if IDs == []:
        print("No data, Headers or Selftests")
    else:    
        print("Found packets:")
        alphabet = list(map(chr, range(ord('a'), ord('z')+1)))
        for i in range(len(positions)):
            print("(", alphabet[i],") ID =", IDs[i], pos_types[i])
        which_spectrum = input("Input a lowercase letter\n")
        k=0
        for k in range(len(alphabet)):
            if(which_spectrum == alphabet[k]):
                break
        
        if pos_types[k] == 'Header':
            the_header = Data_buffer[positions[k]]
            print("ID of the measurement request: ", the_header[0])
            print("Interrupt count:", the_header[1])
            print("Temperature at the end of the measurement: ",the_header[2]*256 + the_header[3] - 273, " °C")
            print("Time of finish: ",the_header[4]*256*256*256 + the_header[5]*256*256 + the_header[6]*256 + the_header[7], " UNIX")
            print("Number of packets:",the_header[8])
            if(the_header[8] == 0):
                print("Number of channels (resolution):",1)
            else:
                print("Number of channels (resolution):",the_header[8]*8)
            print("Lower threshold: ",16*the_header[9]+int(hex(the_header[10])[2], 16))
            print("Higher threshold: ",256*int(hex(the_header[10])[3], 16) + the_header[11])
            print("Reference voltage at the end of the measurement:",the_header[12]*256+the_header[13]," mV")
            checksum = 0
            for i in range(15):
               checksum += bin(the_header[i]).count('1')
            is_checksum_ok = "INVALID"
            if the_header[15] == checksum:
                is_checksum_ok = "OK"
            print("Checksum:",the_header[15], "?=", checksum, is_checksum_ok)

            

            if(the_header[8] == 0):
                the_spectrum = 0
                for i in range(8):
                    the_spectrum += (Data_buffer[positions[k]+1][i+8])*(256**(7-i))
                print("The geiger count:", the_spectrum)
            else:
                the_spectrum = []
                for n in range(positions[k]+1, positions[k]+1 + Data_buffer[positions[k]][8]):
                    grouped_bytes = []
                    for m in range(8):
                        grouped_bytes.append(256 * Data_buffer[n][m*2] + Data_buffer[n][m*2+1])
                    the_spectrum += grouped_bytes
                print("Spectrum contents:", the_spectrum)
                sum = 0
                for i in range(len(the_spectrum)):
                    sum += the_spectrum[i]
                print("Total number of peaks:", sum)
                channel_number = []
                for i in range(len(the_spectrum)):
                    channel_number.append(i)
                

                #moving average calculation:
                '''
                xs = []
                ys = []
                for i in range(3, len(the_spectrum)-3):
                    xs.append(i)
                    ys.append(np.average(the_spectrum[i-3:i+4]))'''

                #low pass filter
                parameter = 2
                while (parameter < 0) or (parameter > 1) or (parameter == ''):
                    parameter = input("\nGive a smoothing parameter for the low pass filter: 0<=p<=1, \nenter nothing to discard\n")
                    if (parameter == ''):
                        break
                    parameter = float(parameter)

                #50th order polinom regression -not so good
                '''coef_row = []
                b = []
                for i in range(len(the_spectrum)):
                    temp = []
                    for j in range(50):
                        temp.append(np.float64(i**j))
                    coef_row.append(temp)
                    b.append(np.float64(the_spectrum[i]))

                solution = np.linalg.matmul(np.linalg.matmul(np.linalg.inv(np.linalg.matmul(np.matrix_transpose(coef_row), coef_row)), np.matrix_transpose(coef_row)), b)
                s = np.matrix.tolist(solution)

                ys = []
                xs = []
                for i in range(2048):
                    temp_ys = 0
                    for j in range(50):
                        temp_ys += s[j]*(i*len(b)/2048)**j
                    ys.append(temp_ys)
                    xs.append(i*len(b)/2048)'''

                if (parameter != ''):
                    xs = [0]
                    ys = [0]

                    for i in range(1, len(the_spectrum)-1):
                            xs.append(i)
                            ys.append(parameter * ys[i-1] + (1-parameter) * the_spectrum[i])
                    plt.plot(xs, ys, 'red', linewidth=1)
                
                
                
                plt.bar(channel_number, the_spectrum, color='black', align='center', width = 1)
                plt.title('Spectrum')
                plt.xlabel('Channel number')
                plt.ylabel('Counts')
                plt.show()
                

        if pos_types[k] == 'Selftest':
            the_selftest = Data_buffer[positions[k]]
            print("Results of the Selftest")
            print("ID of the selftest request: ", the_selftest[0])
            print("Temperature: ",the_selftest[1]*256 + the_selftest[2] - 273, " °C")
            print("Number of errors in i2c queue: ", the_selftest[3])
            print("Time of selftest: ",the_selftest[4]*256*256*256 + the_selftest[5]*256*256 + the_selftest[6]*256 + the_selftest[7], " UNIX")
            print("IDs of the following two requests in queue: ID(next1) = ",the_selftest[8], "; ID(next2) =", the_selftest[9])
            print("ID of the next read in i2c queue: ", the_selftest[10])
            print("Reference voltage: ",16*the_selftest[11]+int(hex(the_selftest[12])[2], 16), " mV")
            print("Voltage on the output of the peak holder: ",256*int(hex(the_selftest[12])[3], 16) + the_selftest[13], " mV")
            checksum = 0
            for i in range(15):
               checksum += bin(the_selftest[i]).count('1')
            is_checksum_ok = "INVALID"
            if the_selftest[15] == checksum:
                is_checksum_ok = "OK"
            print("Checksum:",the_selftest[15], "?=", checksum, is_checksum_ok)


def save_data():
    if Data_buffer == []:
        print("No collected data")
    else:
        file_name = input("Name the .cel file (without .cel)\n")
        overwrite = input("Overwrite the file? 0 = No, 1 = Yes, else = abort\n")
        if overwrite == '0' or overwrite == '1':
            if overwrite == '0':
                print("Append to file", file_name + ".cel")
                f = open(file_name + ".cel", "a")
                for packet in range(int(len(Data_buffer))):
                    for channel in range(16):
                        f.write(str(Data_buffer[packet][channel]))
                        if channel != 15:
                            f.write(' ')
                    f.write("\n")
                f.close()
            if overwrite == '1':
                print("Overwrite file", file_name + ".cel")
                f = open(file_name + ".cel", "w")
                for packet in range(int(len(Data_buffer))):
                    for channel in range(16):
                        f.write(str(Data_buffer[packet][channel]))
                        if channel != 15:
                            f.write(' ')
                    f.write("\n")
                f.close() 
        else: print("aborted")

def import_data():
    file_name = input("Which .cel file to import? (without .cel)\n")
    overwrite = input("Overwrite memory buffer? 0 = No, 1 = Yes, else = abort\n")
    if overwrite == '0' or overwrite == '1':
        if overwrite == '1':
            print("Overwriting memory")
            global Data_buffer
            global packet_info
            Data_buffer = []
            packet_info = []
        if overwrite == 0:
            print("Append to memory")
        with open(file_name + ".cel", "r") as f:
            reader = csv.reader(f, delimiter=" ")
            for line in reader:
                items = []
                for k in range(len(line)):
                    items.append(int(line[k]))
                Data_buffer.append(items)
        f.close()
    else:
        print("aborted")
    process_data()


def user_input():
    loopdeloop = 1
    while loopdeloop == 1:

        print("Options:")
        print("[1]. Write / communication loop")
        print("[2]. Command Generator - under construction")
        print("[3]. Read and store data")
        print("[4]. Evaluate and Display data")
        print("[5]. Print stored data")
        print("[6]. Save data")
        print("[7]. Import data")
        print("[8]. Dump memory")
        print("[9]. Clear console")
        print("[10]. Exit program")
        Option = input("Input an integer\n")
        if Option == '1':
            write_loop()
        if Option == '2':
            print("Command Generator does not work")
            #commander()
        if Option == '3':
            read_data()
        if Option == '4':
            Display()
        if Option == '5':
            print_data()
        if Option == '6':
            save_data()
        if Option == '7':
            import_data()
        if Option == '8':
            global Data_buffer
            global packet_info
            Data_buffer = []
            packet_info = []
        if Option == '9':
            clear()
        if Option == '10':
            loopdeloop = 0

user_input()        # Start the program
