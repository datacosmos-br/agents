cmake_minimum_required(VERSION 3.24)
project(ownership_check LANGUAGES CXX)
add_library(ownership_check sample.cpp)
target_compile_features(ownership_check PUBLIC cxx_std_20)
