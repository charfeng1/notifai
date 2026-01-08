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
| 模型大小 | ~650 MB (Q8_0) |
| 文件夹准确率 | 94.0% |
| 优先级准确率 | 83.0% |

### 资源链接

- 🤗 [模型下载 (HuggingFace)](https://huggingface.co/charlesfeng1/qwen3-0.6b-notifai)
- 📊 [训练数据集 (HuggingFace)](https://huggingface.co/datasets/charlesfeng1/notifai-dataset)

### 快速开始

#### 前置要求

- [Git](https://git-scm.com/) + [Git LFS](https://git-lfs.com/)
- [Android Studio](https://developer.android.com/studio) (Ladybug 2024.2+ 推荐)
- Android 手机 (ARM64, Android 8.0+)
- USB 数据线

#### 第一步：克隆仓库

```bash
# 安装 Git LFS（如未安装）
git lfs install

# 克隆仓库（模型 ~650MB，需要几分钟）
git clone https://github.com/charfeng1/notifai.git
cd notifai

# 克隆 llama.cpp 推理引擎
git clone https://github.com/ggerganov/llama.cpp.git
```

#### 第二步：构建 APK

1. 打开 Android Studio
2. 选择 **File → Open**，选择 `notifai/android` 目录
3. 等待 Gradle 同步完成（首次约 2-5 分钟）
4. 点击 **Build → Make Project** 或按 `Ctrl+F9`

#### 第三步：安装到手机

1. 在手机上启用 **开发者选项** 和 **USB 调试**
   - 设置 → 关于手机 → 连续点击"版本号" 7 次
   - 设置 → 开发者选项 → 开启 USB 调试
2. 用 USB 连接手机到电脑
3. 在 Android Studio 工具栏选择你的设备
4. 点击 **Run ▶** 或按 `Shift+F10`

#### 第四步：授权通知访问

首次启动应用时：

1. 点击 **授予通知权限** 按钮
2. 系统会跳转到 **通知访问** 设置页面
3. 找到 **NotifAI** 并开启权限
4. 返回应用，等待模型加载（首次约 10-20 秒）

#### 开始使用

- 发送一条测试通知（如微信消息）
- 通知会自动分类到对应文件夹（Job/Private/Deals/Notices）
- 点击 **+** 可添加自定义文件夹

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Android App                             │
├─────────────────────────────────────────────────────────────┤
│  Jetpack Compose UI  │  MVVM  │  Hilt DI  │  Room DB        │
├─────────────────────────────────────────────────────────────┤
│  NotificationListener  →  ClassificationService             │
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

### 使用示例

应用安装后，授予通知访问权限，即可自动分类通知：

**默认文件夹：**
- **Job** - 工作相关（Slack、Jira、飞书、钉钉）
- **Private** - 个人消息（微信、WhatsApp、短信）
- **Deals** - 促销信息（购物优惠、广告）
- **Notices** - 系统提醒（银行、快递、安全警报）

**智能通知分发：**
- **High** - 立即推送 + 震动提醒
- **Medium** - 队列聚合，每 30 分钟批量推送
- **Low** - 静默处理，仅存储不打扰

**自定义文件夹：** 点击 "+" 添加自定义文件夹，输入名称和描述，AI 自动学习分类。

### 分类输出格式

模型输出 JSON 格式：
```json
{"folder": "Job", "priority": "high"}
```

### 系统要求

- Android 8.0+ (API 26+)
- ARM64 处理器
- 2GB+ 可用存储空间
- 2GB+ RAM

### 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开源协议

Apache 2.0 License

### 致谢

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - 高性能 LLM 推理引擎
- [Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) - 优秀的开源基座模型
- [llama.rn](https://github.com/mybigday/llama.rn) - 多架构构建灵感来源
- [Unsloth](https://github.com/unslothai/unsloth) - 高效 LoRA 微调框架

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
| Model Size | ~650 MB (Q8_0) |
| Folder Accuracy | 94.0% |
| Priority Accuracy | 83.0% |

### Resources

- 🤗 [Model Download (HuggingFace)](https://huggingface.co/charlesfeng1/qwen3-0.6b-notifai)
- 📊 [Training Dataset (HuggingFace)](https://huggingface.co/datasets/charlesfeng1/notifai-dataset)

### Quick Start

#### Prerequisites

- [Git](https://git-scm.com/) + [Git LFS](https://git-lfs.com/)
- [Android Studio](https://developer.android.com/studio) (Ladybug 2024.2+ recommended)
- Android phone (ARM64, Android 8.0+)
- USB cable

#### Step 1: Clone the Repository

```bash
# Install Git LFS (if not already installed)
git lfs install

# Clone the repo (model is ~650MB, takes a few minutes)
git clone https://github.com/charfeng1/notifai.git
cd notifai

# Clone llama.cpp inference engine
git clone https://github.com/ggerganov/llama.cpp.git
```

#### Step 2: Build the APK

1. Open Android Studio
2. Select **File → Open**, navigate to the `notifai/android` directory
3. Wait for Gradle sync to complete (first time takes 2-5 minutes)
4. Click **Build → Make Project** or press `Ctrl+F9`

#### Step 3: Install on Your Phone

1. Enable **Developer Options** and **USB Debugging** on your phone:
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable USB Debugging
2. Connect your phone to your computer via USB
3. Select your device in the Android Studio toolbar
4. Click **Run ▶** or press `Shift+F10`

#### Step 4: Grant Notification Access

On first launch:

1. Tap the **Grant Notification Permission** button
2. You'll be redirected to the **Notification Access** settings page
3. Find **NotifAI** and enable the permission
4. Return to the app and wait for the model to load (first time takes ~10-20 seconds)

#### Start Using

- Send a test notification (e.g., a WeChat or WhatsApp message)
- Notifications are automatically classified into folders (Job/Private/Deals/Notices)
- Tap **+** to add custom folders

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Android App                             │
├─────────────────────────────────────────────────────────────┤
│  Jetpack Compose UI  │  MVVM  │  Hilt DI  │  Room DB        │
├─────────────────────────────────────────────────────────────┤
│  NotificationListener  →  ClassificationService             │
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

### Usage

After installation, grant notification access permission and the app will automatically classify notifications:

**Default Folders:**
- **Job** - Work-related (Slack, Jira, Feishu, DingTalk)
- **Private** - Personal messages (WeChat, WhatsApp, SMS)
- **Deals** - Promotions (shopping deals, ads)
- **Notices** - System alerts (banking, delivery, security)

**Smart Notification Dispatch:**
- **High** - Immediate push + vibration alert
- **Medium** - Queued, batched every 30 minutes
- **Low** - Silent handling, stored only (no interruption)

**Custom Folders:** Tap "+" to add custom folders with name and description. AI learns to classify automatically.

### Classification Output Format

Model outputs JSON:
```json
{"folder": "Job", "priority": "high"}
```

### System Requirements

- Android 8.0+ (API 26+)
- ARM64 processor
- 2GB+ available storage
- 2GB+ RAM

### Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### License

Apache 2.0 License

### Acknowledgments

- [llama.cpp](https://github.com/ggerganov/llama.cpp) - High-performance LLM inference
- [Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) - Excellent open-source base model
- [llama.rn](https://github.com/mybigday/llama.rn) - Multi-arch build inspiration
- [Unsloth](https://github.com/unslothai/unsloth) - Efficient LoRA fine-tuning framework

---

**Contest Submission**: 上海开源信息技术协会 - 赛道一（开源大模型 × GPU 应用创新）

**Last Updated**: January 8, 2026
