cmake_minimum_required (VERSION 2.6)
project (comp316)

set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS} "-mavx2 -pg -ggdb -O3") 
add_definitions(-DCHUNK_MALLOC)

########################################################################
# Build utility
########################################################################
add_executable(n-waypuzzle n-waypuzzle.c list_fifo.c challoc/challoc.c)

target_link_libraries(n-waypuzzle
    m
    pthread
    ${CMAKE_SOURCE_DIR}/Cuckoo-hash/src/.libs/libcuckoo_hash.a
)


IF (UNIX)
  ADD_CUSTOM_TARGET (distclean @echo cleaning for source distribution)
  SET(DISTCLEANED
   cmake.depends
   cmake.check_depends
   CMakeCache.txt
   cmake.check_cache
   *.cmake
   Makefile
   core core.*
   gmon.out
   *~
  )
  
  ADD_CUSTOM_COMMAND(
    DEPENDS clean
    COMMENT "distribution clean"
    COMMAND rm
    ARGS    -Rf CMakeTmp ${DISTCLEANED}
    TARGET  distclean
  )
ENDIF(UNIX)

