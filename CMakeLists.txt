cmake_minimum_required(VERSION 3.8)
cmake_policy(SET CMP0048 NEW)

project("PM Invariant Generation" VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
separate_arguments(LLVM_DEFINITIONS_LIST NATIVE_COMMAND ${LLVM_DEFINITIONS})
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})

# Define the path to the opt and llc executables
set(LLVM_OPT_EXE "${LLVM_TOOLS_BINARY_DIR}/opt")
set(LLVM_LLC_EXE "${LLVM_TOOLS_BINARY_DIR}/llc")
set(LLVM_LINK_EXE "${LLVM_TOOLS_BINARY_DIR}/llvm-link")
find_package(PkgConfig)


pkg_check_modules(Z3 REQUIRED)
pkg_check_modules(boost REQUIRED)

if(WIN32 OR CYGWIN)
    set(LLVM_LINK_COMPONENTS Core Support)
endif()

add_subdirectory(Transform)
