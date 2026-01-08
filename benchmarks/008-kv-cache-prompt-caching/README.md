# 基准测试 008: KV Cache 系统提示缓存优化

**日期:** 2026-01-08
**模型:** Qwen3-0.6B 微调版
**优化:** KV Cache 系统提示缓存
**硬件:** Google Pixel (ARMv8.2 + DotProd)

## 测试结果

通过缓存系统提示的 KV Cache 状态，显著减少了后续推理的预填充时间。

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 首次推理 | ~3-5 秒 | ~2.5 秒 | - |
| 后续推理 | ~3-5 秒 | **~1.3 秒** | **~50%** |
| 预填充 tokens | 203 | 35 | -83% |
| 首 token 延迟 | ~1600ms | ~380ms | **-76%** |

## 优化原理

### 问题分析

每次通知分类的提示包含：
- **系统提示** (~184 tokens): 文件夹描述、优先级定义、输出格式
- **用户消息** (~35 tokens): App名称、标题、正文

原始实现每次推理都重新处理完整提示（~219 tokens），但系统提示在每次分类中都是**完全相同的**。

### 解决方案

1. **首次推理**: 处理完整系统提示，将 KV Cache 状态保存
2. **后续推理**: 复用系统提示的 KV Cache，只处理用户消息

```
优化前: [系统提示 184 tokens] + [用户消息 35 tokens] = 219 tokens 预填充
优化后: [KV Cache 复用] + [用户消息 35 tokens] = 35 tokens 预填充
```

## 实现细节

### 1. PromptBuilder 拆分

```kotlin
// 系统提示（可缓存）
suspend fun buildSystemPrompt(): String

// 用户消息（每次不同）
fun buildUserMessage(appName: String, title: String, body: String): String
```

### 2. JNI 层缓存接口

```cpp
// 缓存系统提示到 KV Cache
JNIEXPORT jint JNICALL nativeCacheSystemPrompt(JNIEnv*, jobject, jstring);

// 使缓存失效（文件夹/设置变更时）
JNIEXPORT void JNICALL nativeInvalidateCache(JNIEnv*, jobject);

// 检查缓存是否有效
JNIEXPORT jboolean JNICALL nativeIsCacheValid(JNIEnv*, jobject);
```

### 3. 推理路径选择

```cpp
if (g_system_prompt_cached && g_system_prompt_tokens > 0) {
    // 快速路径: 只清除用户消息位置之后的 KV Cache
    llama_memory_seq_rm(kv, 0, g_system_prompt_tokens, -1);
    // 只处理用户消息 tokens
} else {
    // 慢速路径: 处理完整提示
    llama_memory_clear(kv, true);
}
```

### 4. 位置偏移处理

用户消息 tokens 需要从正确的位置开始：

```cpp
for (int j = 0; j < batch_size; j++) {
    int pos = prefill_start_pos + token_idx;  // 从系统提示结束位置开始
    batch.pos[batch.n_tokens] = pos;
    // ...
}
```

## 性能日志示例

### 首次推理（冷启动）
```
LlamaJNI: No system prompt cache, processing full prompt...
LlamaJNI: Tokenized to 203 tokens (prefill start: 0)
LlamaPerf: === PREFILL: 203 tokens in 1593.8 ms (127.4 tok/s) ===
LlamaPerf: === TOTAL: 2499.0 ms ===
```

### 后续推理（缓存命中）
```
LlamaJNI: Using cached system prompt (184 tokens), processing user message only...
LlamaJNI: Tokenized to 35 tokens (prefill start: 184)
LlamaPerf: === PREFILL: 35 tokens in 379.9 ms (92.1 tok/s) ===
LlamaPerf: === TOTAL: 1339.2 ms ===
```

## 缓存失效场景

以下情况会触发缓存重建：
1. 用户修改文件夹设置
2. 用户修改个人偏好指令
3. 应用重启

缓存通过系统提示的 hash 值检测变化，避免不必要的重建。

## 关键发现

1. **预填充是主要瓶颈** - 预填充时间占总推理时间的 60-70%
2. **KV Cache 复用有效** - 减少 83% 的预填充 tokens
3. **首 token 延迟显著降低** - 从 ~1600ms 降至 ~380ms
4. **解码速度不变** - ~17-18 tok/s，不受缓存影响

## 局限性

1. **模型仍输出空 think 标签** - `<think>\n\n</think>` 占用少量 tokens
2. **首次推理无优化** - 仍需完整处理系统提示
3. **内存占用略增** - KV Cache 常驻内存

## 相关文件

- JNI 实现: `android/app/src/main/cpp/llama_jni.cpp`
- Kotlin 接口: `android/app/src/main/java/com/notifai/domain/classifier/LlamaClassifier.kt`
- 提示构建: `android/app/src/main/java/com/notifai/domain/classifier/PromptBuilder.kt`
- 用例调用: `android/app/src/main/java/com/notifai/domain/usecase/ClassifyNotificationUseCase.kt`

## 结论

**状态:** ✅ 优化成功

KV Cache 系统提示缓存将后续推理时间从 3-5 秒降至 ~1.3 秒，提升约 50%。这是一个低成本、高收益的优化，特别适合系统提示固定的场景。

## 下一步

1. **Vulkan GPU 加速** - 利用移动端 GPU 进行矩阵运算
2. **投机解码** - 使用小模型预测减少解码时间
3. **量化优化** - 测试 Q4_K_M 等更激进的量化方案
