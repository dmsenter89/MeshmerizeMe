project (MeshmerizeMe)

cmake_minimum_required(VERSION 3.5)
find_package(Boost 1.5.0 REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})
add_definitions(-std=c++11)

file(GLOB SOURCES "src/*cc")

add_executable(meshmerizeme ${SOURCES})

# How to build a debug version:
# cmake -DCMAKE_BUILD_TYPE=Debug
# different cmake build types are available.
# To use a different compiler, either change the CC and CXX vars
# or use cmake -D CMAKE_C_COMPILER=gcc-4.2 -D CMAKE_CXX_COMPILER=g++-4.2 path/to/your/source
