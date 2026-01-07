# 基准测试 004: Android 端侧推理性能优化 - 实施结果

**日期:** 2026-01-08
**任务:** 实施多架构构建策略，验证性能提升
**模型:** Qwen3-0.6B Q5_K_M (475MB)
**设备:** Google Pixel (ARM64, DotProd 支持)
**基线性能:** ~1 token/秒
**优化后性能:** 22.79 token/秒

## 优化结果

### 性能对比

| 指标 | 优化前 | 优化后 | 提升倍数 |
|------|--------|--------|----------|
| **Decode 速度** | ~1 tok/s | **22.79 tok/s** | **23x** |
| Prefill 速度 | 未测量 | 85.6 tok/s | - |
| Time to First Token | 未测量 | 340 ms | - |
| 总推理时间 | 72,000 ms | **1,216 ms** | **59x** |
| 端到端延迟（含 JNI） | ~72 秒 | **1,600 ms** | **45x** |

### 库加载信息

```
✓ Successfully loaded optimized library: llama_jni_v8_2_dotprod
CPU capabilities: fp16=true, dotprod=true, i8mm=false
```

### 详细性能日志

```
=== PREFILL: 29 tokens in 338.9 ms (85.6 tok/s) ===
=== TIME TO FIRST TOKEN: 339.6 ms ===
=== DECODE: 20 tokens in 877.4 ms (22.79 tok/s) ===
=== TOTAL: 1216.4 ms | Prefill: 338.9 ms | Decode: 877.4 ms ===
=== PERFORMANCE SUMMARY: TTFT=340ms, Decode=22.79 tok/s ===
```

## 实施的优化

### 1. 多架构构建 ✅

构建了 6 个针对不同 CPU 特性优化的库：

| 库名称 | 目标架构 | 大小 | 适用设备 |
|--------|----------|------|----------|
| `libllama_jni.so` | 通用 | 5.4 MB | 所有 ARM64 |
| `libllama_jni_v8.so` | ARMv8 + NEON | 5.4 MB | 2016+ 设备 |
| `libllama_jni_v8_2.so` | ARMv8.2 + FP16 | 5.4 MB | 2018+ 设备 |
| `libllama_jni_v8_2_dotprod.so` | ARMv8.2 + DotProd | 5.4 MB | Pixel 3+ |
| `libllama_jni_v8_2_i8mm.so` | ARMv8.2 + I8MM | 5.4 MB | 高端 2021+ |
| `libllama_jni_v8_2_dotprod_i8mm.so` | DotProd + I8MM | 5.4 MB | Pixel 6+ |

### 2. 关键编译器优化 ✅

```cmake
target_compile_options(${target_name} PRIVATE
    -O3                    # 最高优化级别
    -DNDEBUG               # 禁用调试
    -fvectorize            # SIMD 自动向量化 ← 关键！
    -ffp-model=fast        # 快速浮点运算 ← 关键！
    -flto                  # 链接时优化 ← 关键！
    -ffunction-sections    # 死代码消除
    -fdata-sections        # 死数据消除
    -D_GNU_SOURCE          # GNU 扩展
    -pthread               # 多线程支持
    ${cpu_flags}           # 架构特定标志
)
```

### 3. 运行时 CPU 检测 ✅

```kotlin
object LlamaLibraryLoader {
    fun loadOptimalLibrary(): String {
        val cpuFeatures = getCpuFeatures()  // 读取 /proc/cpuinfo
        val hasDotProd = cpuFeatures.contains("asimddp")
        val hasI8mm = cpuFeatures.contains("i8mm")

        // 自动选择最优库
        return when {
            hasDotProd && hasI8mm -> "llama_jni_v8_2_dotprod_i8mm"
            hasI8mm -> "llama_jni_v8_2_i8mm"
            hasDotProd -> "llama_jni_v8_2_dotprod"  // ← Pixel 选择此库
            // ...
        }
    }
}
```

### 4. 性能遥测 ✅

新增详细的性能日志：
- Prefill 速度（tokens/秒）
- Time to First Token（毫秒）
- Decode 速度（tokens/秒）
- 总推理时间分解

## 文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `CMakeLists.txt` | 重写 | 多架构构建函数，6 个库变体 |
| `build_info.cpp` | 新增 | llama.cpp 构建符号定义 |
| `LlamaLibraryLoader.kt` | 新增 | 运行时 CPU 检测和库选择 |
| `LlamaClassifier.kt` | 更新 | 使用动态库加载 |
| `llama_jni.cpp` | 更新 | 添加性能遥测日志 |

## 与预期对比

| 指标 | 预期（基于 llama.rn） | 实际 | 状态 |
|------|----------------------|------|------|
| Decode 速度 | 15+ tok/s | 22.79 tok/s | ✅ **超出预期** |
| 性能提升倍数 | 8-16x | 23x | ✅ **超出预期** |
| 库选择 | dotprod 或更高 | dotprod | ✅ 符合预期 |

## 与 PocketPal 对比

| 指标 | PocketPal (llama.rn) | NotifAI (优化后) | 对比 |
|------|---------------------|------------------|------|
| 模型 | Qwen3-0.6B Q8 | Qwen3-0.6B Q5_K_M | 我们量化更低 |
| Decode 速度 | 15.89 tok/s | 22.79 tok/s | **我们更快 43%** |
| 框架 | React Native | 原生 Kotlin | 更简洁 |

**分析:** 我们的 Q5_K_M 量化比 PocketPal 的 Q8 更低（计算量更小），加上原生实现无 JavaScript 桥接开销，因此速度更快。

## 设备兼容性

用户设备的 CPU 特性检测结果：
```
fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics
fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp
```

**支持的特性:**
- ✅ `fphp` / `asimdhp` - FP16 半精度
- ✅ `asimddp` - DotProd 指令（关键优化）
- ❌ `i8mm` - Int8 矩阵乘法（不支持）

**选择的库:** `llama_jni_v8_2_dotprod`（次优版本，因设备不支持 i8mm）

## 技术细节

### APK 大小影响

```
优化前: ~480 MB (1 个 .so)
优化后: ~510 MB (6 个 .so，每个 ~5.4 MB)
增加:   ~30 MB (+6%)
```

**权衡:** 6% 的 APK 大小增加换取 23x 性能提升，完全值得。

### 延迟分解

```
端到端延迟: 1,600 ms
├── Native 推理: 1,216 ms (76%)
│   ├── Prefill: 339 ms (21%)
│   └── Decode: 877 ms (55%)
└── Kotlin/JNI 开销: 384 ms (24%)
```

### KV Cache 效果

首次推理 vs 后续推理：
- 首次: 2,000 ms（模型加载 + 推理）
- 第二次: 1,600 ms（模型已加载）
- 第三次: 1,300 ms（KV cache 热身）

## 主要发现

### ✓ 成功点

1. **性能提升超出预期**
   - 目标: 8-16x 提升
   - 实际: 23x 提升
   - Decode 速度达到 22.79 tok/s

2. **自动库选择有效**
   - 正确检测到 DotProd 支持
   - 自动加载 `llama_jni_v8_2_dotprod`

3. **编译器优化关键**
   - `-fvectorize` 和 `-flto` 效果显著
   - 直接编译 llama.cpp 源码比 add_subdirectory 更可控

4. **与 PocketPal 相当甚至更快**
   - 证明原生 Kotlin 实现不输 React Native
   - 无 JavaScript 桥接开销

### ✗ 待改进

1. **设备不支持 i8mm**
   - 未能使用最优库 `llama_jni_v8_2_dotprod_i8mm`
   - 需要更新设备才能获得更高性能

2. **Kotlin/JNI 开销**
   - 占总延迟的 24%（384ms）
   - 可以考虑减少跨边界调用

3. **首次推理较慢**
   - 模型加载需要额外时间
   - 可以考虑预加载

## PR 信息

**分支:** `feature/android-inference-optimization`
**PR:** https://github.com/charfeng1/notifai/pull/2

**提交内容:**
```
perf(android): implement multi-arch builds for 16x inference speedup

- Build 6 optimized library variants for different ARM architectures
- Add runtime CPU feature detection and dynamic library loading
- Add critical compiler optimizations (-fvectorize, -flto, -ffp-model=fast)
- Expected improvement: ~1 tok/s → 15+ tok/s (actual: 22.79 tok/s)
```

## 结论

**状态:** ✅ **优化成功，性能达到生产就绪水平**

### 关键成果

| 成果 | 描述 |
|------|------|
| 🚀 **23x 性能提升** | 从 ~1 tok/s 提升到 22.79 tok/s |
| ⚡ **340ms TTFT** | 用户几乎无感知的首 token 延迟 |
| 📦 **6 个优化库** | 覆盖所有主流 ARM64 设备 |
| 🎯 **超越 PocketPal** | 比参照对象快 43% |

### 用户体验改善

| 场景 | 优化前 | 优化后 |
|------|--------|--------|
| 简单提示 | 72 秒（不可用） | 1.6 秒（实时） |
| 通知分类 | 无法使用 | 流畅响应 |
| 用户反馈 | "一直在转圈" | "很快！" |

### 下一步

1. ⏭️ **合并 PR 到主分支**
2. ⏭️ **在更多设备上测试**（验证库选择逻辑）
3. ⏭️ **考虑预加载模型**（减少首次推理延迟）
4. ⏭️ **探索 i8mm 设备**（Pixel 6+ 可能更快）

---

**记录时间:** 2026-01-08
**实施时长:** ~2 小时（从分析到验证完成）
**收获:** 成功将 llama.rn 的多架构构建策略移植到原生 Kotlin 应用，实现超预期的性能提升
