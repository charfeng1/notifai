# NotifAI - 端侧智能通知分类

[English](#english) | [中文](#中文)

---

## 中文

使用端侧 AI 大模型自动分类手机通知，完全离线运行，保护用户隐私。

### 核心特性

- **完全端侧推理** - 通知内容永不离开设备，零隐私风险
- **微调 Qwen3-0.6B** - 94% 文件夹准确率，83% 优先级准确率
- **23x 性能优化** - 多架构编译 + KV 缓存，1.3 秒完成分类
- **自定义文件夹** - 涌现泛化能力，无需重新训练

### 性能指标

| 指标 | 数值 |
|------|------|
| 分类延迟 | 1.3 秒 |
| Decode 速度 | 22.79 tok/s |
| 模型大小 | 475 MB |
| 文件夹准确率 | 94.0% |
| 优先级准确率 | 83.0% |

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/charfeng1/notifai.git
cd notifai

# 2. 下载模型
pip install huggingface-hub
huggingface-cli download charfeng1/qwen3-0.6b-notif-gguf \
  --local-dir android/app/src/main/assets/models/

# 3. 克隆 llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git

# 4. 用 Android Studio 打开 android/ 目录，构建并运行
```

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Android App                              │
├─────────────────────────────────────────────────────────────┤
│  Jetpack Compose UI  │  MVVM  │  Hilt DI  │  Room DB        │
├─────────────────────────────────────────────────────────────┤
│  NotificationListener  →  ClassificationService              │
├─────────────────────────────────────────────────────────────┤
│  LlamaClassifier (Kotlin)  →  JNI  →  llama.cpp (C++)       │
├─────────────────────────────────────────────────────────────┤
│  Multi-Arch Libraries: Generic │ ARMv8 │ DotProd │ I8MM     │
└─────────────────────────────────────────────────────────────┘
```

### 项目结构

```
notifai/
├── android/                    # Android 应用源码
│   ├── app/src/main/
│   │   ├── java/com/notifai/   # Kotlin 源码
│   │   ├── cpp/                # JNI 层 (llama_jni.cpp)
│   │   └── assets/models/      # GGUF 模型文件
├── data/                       # 合成训练数据集 (16K 条)
├── benchmarks/                 # 性能基准测试报告
├── docs/                       # 项目文档
├── llama.cpp/                  # llama.cpp 推理引擎
└── scripts/                    # 数据处理和微调脚本
```

### 基准测试

| 基准 | 描述 | 状态 |
|------|------|------|
| 001 | Qwen3-0.6B 基线测试 | ✅ |
| 002 | FunctionGemma 基线测试 | ✅ |
| 004 | Android 推理优化 (23x) | ✅ |
| 006 | Qwen3-0.6B 微调 | ✅ |
| 007 | 涌现分类能力测试 | ✅ |
| 008 | KV Cache 缓存优化 (50%) | ✅ |

### 开源协议

Apache 2.0 License

### 致谢

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - 高性能 LLM 推理引擎
- [Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) - 优秀的开源基座模型
- [llama.rn](https://github.com/mybigday/llama.rn) - 多架构构建灵感来源

---

## English

AI-powered notification organizer for Android using on-device Qwen3-0.6B LLM. Fully offline, privacy-first.

### Key Features

- **Fully On-Device** - Notifications never leave your phone, zero privacy risk
- **Fine-tuned Qwen3-0.6B** - 94% folder accuracy, 83% priority accuracy
- **23x Performance Boost** - Multi-arch build + KV cache, 1.3s classification
- **Custom Folders** - Emergent generalization, no retraining needed

### Performance

| Metric | Value |
|--------|-------|
| Classification Latency | 1.3 seconds |
| Decode Speed | 22.79 tok/s |
| Model Size | 475 MB |
| Folder Accuracy | 94.0% |
| Priority Accuracy | 83.0% |

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/charfeng1/notifai.git
cd notifai

# 2. Download the model
pip install huggingface-hub
huggingface-cli download charfeng1/qwen3-0.6b-notif-gguf \
  --local-dir android/app/src/main/assets/models/

# 3. Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git

# 4. Open android/ in Android Studio, build and run
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Android App                              │
├─────────────────────────────────────────────────────────────┤
│  Jetpack Compose UI  │  MVVM  │  Hilt DI  │  Room DB        │
├─────────────────────────────────────────────────────────────┤
│  NotificationListener  →  ClassificationService              │
├─────────────────────────────────────────────────────────────┤
│  LlamaClassifier (Kotlin)  →  JNI  →  llama.cpp (C++)       │
├─────────────────────────────────────────────────────────────┤
│  Multi-Arch Libraries: Generic │ ARMv8 │ DotProd │ I8MM     │
└─────────────────────────────────────────────────────────────┘
```

### Repository Structure

```
notifai/
├── android/                    # Android app source code
│   ├── app/src/main/
│   │   ├── java/com/notifai/   # Kotlin source
│   │   ├── cpp/                # JNI layer (llama_jni.cpp)
│   │   └── assets/models/      # GGUF model files
├── data/                       # Synthetic training dataset (16K entries)
├── benchmarks/                 # Performance benchmark reports
├── docs/                       # Project documentation
├── llama.cpp/                  # llama.cpp inference engine
└── scripts/                    # Data processing and fine-tuning scripts
```

### Benchmarks

| Benchmark | Description | Status |
|-----------|-------------|--------|
| 001 | Qwen3-0.6B Baseline | ✅ |
| 002 | FunctionGemma Baseline | ✅ |
| 004 | Android Inference Optimization (23x) | ✅ |
| 006 | Qwen3-0.6B Fine-tuning | ✅ |
| 007 | Emergent Classification Test | ✅ |
| 008 | KV Cache Optimization (50%) | ✅ |

### License

Apache 2.0 License

### Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - High-performance LLM inference
- [Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) - Excellent open-source base model
- [llama.rn](https://github.com/mybigday/llama.rn) - Multi-arch build inspiration

---

**Contest Submission**: 上海开源信息技术协会 - 赛道一（开源大模型 × GPU 应用创新）

**Last Updated**: January 8, 2026
