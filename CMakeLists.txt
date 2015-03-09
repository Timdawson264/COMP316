cmake_minimum_required (VERSION 2.6)
project (comp316)

set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS} "-msse4 -pg")

########################################################################
# Build utility
########################################################################
add_executable(npuzzle n-waypuzzle.c libchash/libchash.c crc64.c)

target_link_libraries(npuzzle
    m
    pthread
)
