cmake_minimum_required(VERSION 3.22.1)
project("notifai_llama")

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED true)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED true)

# Path to llama.cpp
set(LLAMA_CPP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../../llama.cpp")

# Configure for Android ARM64 - explicitly tell CMake we're cross-compiling
set(CMAKE_CROSSCOMPILING TRUE)
# Let llama.cpp auto-detect ARM NEON optimizations for armv8-a

# Set 16KB page alignment for Android 15+ compatibility
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -Wl,-z,max-page-size=16384")

# Include llama.cpp build system
add_subdirectory(${LLAMA_CPP_DIR} build-llama EXCLUDE_FROM_ALL)

# JNI wrapper library
add_library(llama_jni SHARED
    llama_jni.cpp
)

target_include_directories(llama_jni PRIVATE
    ${LLAMA_CPP_DIR}
    ${LLAMA_CPP_DIR}/common
    ${LLAMA_CPP_DIR}/include
    ${LLAMA_CPP_DIR}/ggml/include
    ${LLAMA_CPP_DIR}/ggml/src
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

target_link_options(llama_jni PRIVATE
    -Wl,-z,max-page-size=16384
)

target_link_libraries(llama_jni
    llama
    android
    log
)
