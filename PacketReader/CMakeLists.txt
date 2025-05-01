cmake_minimum_required(VERSION 3.31)
project(PacketReader C)

set(CMAKE_C_STANDARD 11)

add_executable(PacketReader main.c
        Commands.c
        Commands.h)
