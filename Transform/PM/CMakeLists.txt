cmake_minimum_required(VERSION 3.8)

project("PM Invariant Generation Trace Generation" VERSION 1.0)

add_library(LLVMPMC SHARED
        pm.cpp
        pm.h)
