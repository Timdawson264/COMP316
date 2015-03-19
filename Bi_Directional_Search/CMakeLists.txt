cmake_minimum_required (VERSION 2.6)
project (Bi_Directional_Search)

set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS} "-mavx2 -std=gnu99 -pg -ggdb -O3") 
add_definitions(-DCHUNK_MALLOC)

########################################################################
# Build utility
########################################################################
add_executable(n-waypuzzle
    n-waypuzzle.c
    list_fifo.c
    challoc/challoc.c
    Cuckoo-hash/src/cuckoo_hash.c
    Cuckoo-hash/src/lookup3.c
)

target_link_libraries(n-waypuzzle
    m
    pthread
)
