cmake_minimum_required(VERSION 3.22.1)
project("notifai_llama")

# Path to llama.cpp (will need to clone as git submodule or copy)
set(LLAMA_CPP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../llama.cpp")

# Include llama.cpp headers
include_directories(
    ${LLAMA_CPP_DIR}
    ${LLAMA_CPP_DIR}/common
    ${LLAMA_CPP_DIR}/include
    ${LLAMA_CPP_DIR}/ggml/include
)

# Add llama.cpp source files
file(GLOB LLAMA_SOURCES
    "${LLAMA_CPP_DIR}/src/*.cpp"
    "${LLAMA_CPP_DIR}/ggml/src/*.c"
    "${LLAMA_CPP_DIR}/common/*.cpp"
)

# JNI wrapper library
add_library(llama_jni SHARED
    llama_jni.cpp
    ${LLAMA_SOURCES}
)

target_compile_definitions(llama_jni PRIVATE
    GGML_USE_CPU=1
    NDEBUG=1
)

target_compile_options(llama_jni PRIVATE
    -std=c++17
    -O3
    -ffast-math
    -funroll-loops
)

target_link_libraries(llama_jni
    android
    log
)
