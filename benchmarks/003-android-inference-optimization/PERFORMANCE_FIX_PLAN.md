# Performance Fix Plan - llama.rn Build Strategy

## Problem
Our current implementation: ~1 token/second
PocketPal with llama.rn: 8.12 tokens/second (8x faster)

## Root Cause
We build only ONE generic library with minimal optimizations.
llama.rn builds 5 optimized libraries with architecture-specific code and runtime selection.

## Solution: Copy llama.rn's Build Strategy (Keep Kotlin Code)

### What We Need to Copy from llama.rn:

#### 1. Multi-Architecture Build (CMakeLists.txt)
```cmake
# Build 5 different optimized libraries
build_rnllama_library("rnllama_v8" "arm" "-march=armv8-a")
build_rnllama_library("rnllama_v8_2" "arm" "-march=armv8.2-a")
build_rnllama_library("rnllama_v8_2_dotprod" "arm" "-march=armv8.2-a+dotprod")
build_rnllama_library("rnllama_v8_2_i8mm" "arm" "-march=armv8.2-a+i8mm")
build_rnllama_library("rnllama_v8_2_dotprod_i8mm" "arm" "-march=armv8.2-a+dotprod+i8mm")
```

#### 2. Critical Compiler Flags
```cmake
target_compile_options(${target_name} PRIVATE
    -DLM_GGML_USE_CPU
    -DLM_GGML_USE_CPU_REPACK      # ← Optimized memory layout
    -pthread
    -fvectorize                    # ← Auto-vectorization
    -ffp-model=fast                # ← Fast floating point
    -fno-finite-math-only
    -flto                          # ← Link-time optimization
    -D_GNU_SOURCE
    -O3
    -DNDEBUG
    -ffunction-sections
    -fdata-sections
)
```

#### 3. Architecture-Specific Optimized Code
```cmake
# Hand-optimized ARM assembly for quantization
if (NOT ${arch} STREQUAL "generic")
    set(SOURCE_FILES_ARCH
        ${RNLLAMA_LIB_DIR}/ggml-cpu/arch/${arch}/quants.c
        ${RNLLAMA_LIB_DIR}/ggml-cpu/arch/${arch}/repack.cpp
    )
endif()
```

#### 4. Runtime Library Selection (Kotlin)
Copy `RNLlama.java:184-223` logic to detect CPU features:
```kotlin
object LlamaLibraryLoader {
    fun loadOptimalLibrary(): String {
        val cpuFeatures = getCpuFeatures()
        val hasDotProd = cpuFeatures.contains("dotprod")
        val hasI8mm = cpuFeatures.contains("i8mm")

        return when {
            hasDotProd && hasI8mm -> {
                System.loadLibrary("llama_jni_v8_2_dotprod_i8mm")
                "llama_jni_v8_2_dotprod_i8mm"
            }
            hasDotProd -> {
                System.loadLibrary("llama_jni_v8_2_dotprod")
                "llama_jni_v8_2_dotprod"
            }
            else -> {
                System.loadLibrary("llama_jni_v8")
                "llama_jni_v8"
            }
        }
    }

    private fun getCpuFeatures(): String {
        return File("/proc/cpuinfo").readText()
    }
}
```

### Files to Modify:

1. **E:\projects\notif\android\app\src\main\cpp\CMakeLists.txt**
   - Replace entire build configuration with llama.rn's multi-arch strategy
   - Add all 5 library builds
   - Add critical compiler flags

2. **E:\projects\notif\android\app\build.gradle.kts**
   - Update to build all 5 ABIs
   - Remove our current simple flags

3. **New File: E:\projects\notif\android\app\src\main\java\com\notifai\domain\classifier\LlamaLibraryLoader.kt**
   - CPU feature detection
   - Runtime library selection logic

4. **E:\projects\notif\android\app\src\main\java\com\notifai\domain\classifier\LlamaClassifier.kt**
   - Call LlamaLibraryLoader before initialization

### Effort Estimate:
- **Time**: 2-3 hours of CMake configuration + testing
- **Complexity**: Medium (CMake expertise required)
- **Risk**: Low (worst case: falls back to current performance)
- **Kotlin Code Changes**: Minimal (just library loading logic)

### Expected Result:
- Current: ~1 token/second
- After fix: 5-8 tokens/second (matches llama.rn)
- **Your Kotlin code stays exactly the same!**

### Alternative: Switch to Different Framework

If CMake configuration proves too complex, consider:

1. **ExecuTorch** (Facebook/Meta)
   - Reports: 44.5 tokens/sec on Pixel 8 Pro
   - Different build system, but similar Kotlin JNI integration
   - File: https://github.com/pytorch/executorch

2. **MediaPipe LLM Inference** (Google)
   - Official Android support
   - May access NPU on Pixel devices
   - File: https://developers.google.com/mediapipe/solutions/genai/llm_inference

## Recommended Approach:

**Option 1 (Recommended): Copy llama.rn build system**
- Pros: Keep all your Kotlin code, proven 8x speedup
- Cons: Complex CMake configuration

**Option 2: Switch to ExecuTorch**
- Pros: Potentially even faster (44.5 tok/s), official Meta support
- Cons: Complete framework change, different model format

## Next Steps:

1. Decide which approach to take
2. If copying llama.rn build: Start with CMakeLists.txt modifications
3. If switching framework: Research ExecuTorch or MediaPipe integration
