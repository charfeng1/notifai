# Notifai Android App

On-device AI-powered notification organizer using Qwen3-0.6B and llama.cpp.

## Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- Android SDK 28+
- NDK 26.1.10909125 (for building llama.cpp)
- Pixel 7 Pro or similar device for testing
- ~500MB free space (for model)

## Build Instructions

### 1. Setup llama.cpp

```bash
# Clone llama.cpp into project root
cd ..
git clone https://github.com/ggerganov/llama.cpp.git

# The CMakeLists.txt expects llama.cpp at ../llama.cpp relative to app/src/main/cpp/
```

### 2. Get the Model

The model file is NOT in git (too large). Download it:

```bash
cd ../models
hf download unsloth/Qwen3-0.6B-GGUF Qwen3-0.6B-Q5_K_M.gguf --local-dir .

# Copy to Android assets
cp Qwen3-0.6B-Q5_K_M.gguf ../android/app/src/main/assets/models/
```

### 3. Open in Android Studio

1. Open Android Studio
2. File → Open → Select `android/` directory
3. Wait for Gradle sync
4. Build → Make Project

### 4. Run on Device

1. Connect Pixel 7 Pro via USB
2. Enable USB Debugging
3. Run → Run 'app'

## Project Structure

```
app/src/main/
├── java/com/notifai/
│   ├── data/           # Room database, repositories
│   ├── domain/         # Business logic, LLM classifier
│   ├── service/        # NotificationListenerService
│   ├── ui/             # Jetpack Compose screens
│   └── di/             # Hilt dependency injection
├── cpp/                # llama.cpp JNI wrapper
├── assets/models/      # Qwen3-0.6B model file
└── res/                # Android resources
```

## Key Features

- **P0 Features** (MVP):
  - NotificationListenerService captures notifications
  - On-device Qwen3-0.6B classification (<1s)
  - Room database storage
  - Folder view UI (Work, Personal, Promotions, Alerts)
  - App selection (choose which apps to monitor)

- **P2 Features** (Polish):
  - Custom folder creation
  - Personal instructions for classification
  - GBNF grammar support (Phase 2 - eliminates hallucinations)

## Performance

- **Classification Speed**: Target <1 second on Pixel 7 Pro
- **Model**: Qwen3-0.6B Q5_K_M (~424MB)
- **Threads**: 8 (utilizes all cores)
- **Quantization**: 5-bit for speed/quality balance

## Architecture

**Pattern**: MVVM + Repository + Use Cases

**Tech Stack**:
- Kotlin 1.9.22
- Jetpack Compose + Material3
- Room Database 2.6.1
- Hilt 2.50
- llama.cpp (latest)

## Troubleshooting

**Build fails with "cmake: command not found"**:
- Install CMake via Android Studio SDK Manager

**Model not found error**:
- Ensure model is in `app/src/main/assets/models/Qwen3-0.6B-Q5_K_M.gguf`

**Slow inference (>2 seconds)**:
- Check thread count in llama_jni.cpp (should be 8)
- Ensure using Q5_K_M quantization, not F16

**Service gets killed**:
- Grant battery optimization exemption in Settings
- Check foreground service is running

## License

Open source for contest submission. See root LICENSE file.
