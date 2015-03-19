cmake_minimum_required(VERSION 2.6)
project (COMP316)
 
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR})
 
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR})
 
#et(PROJECT_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/include)
 
#include_directories("${PROJECT_INCLUDE_DIR}")
#include_directories("${PROJECT_SOURCE_DIR}")
 
add_subdirectory(Bi_Directional_Search)
#add_subdirectory(project2)


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
   CMakeFiles
  )
  
  ADD_CUSTOM_COMMAND(
    DEPENDS clean
    COMMENT "distribution clean"
    COMMAND rm
    ARGS    -Rf CMakeTmp ${DISTCLEANED}
    TARGET  distclean
  )
  
ENDIF(UNIX)
