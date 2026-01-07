#include <jni.h>
#include <android/log.h>
#include <string>
#include <vector>
#include <cstring>

// Include llama.cpp headers
#include "llama.h"
#include "sampling.h"

#define LOG_TAG "LlamaJNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// Global model and context
static llama_model* g_model = nullptr;
static llama_context* g_ctx = nullptr;
static llama_sampler* g_sampler = nullptr;

extern "C" {

JNIEXPORT jboolean JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeInit(
        JNIEnv* env, jobject thiz, jstring model_path) {

    const char* path = env->GetStringUTFChars(model_path, nullptr);
    LOGI("Loading model from: %s", path);

    // Initialize backend
    llama_backend_init();

    // Model parameters
    llama_model_params model_params = llama_model_default_params();
    model_params.n_gpu_layers = 0; // CPU-only for Android

    // Load model
    g_model = llama_load_model_from_file(path, model_params);
    env->ReleaseStringUTFChars(model_path, path);

    if (!g_model) {
        LOGE("Failed to load model");
        return JNI_FALSE;
    }

    // Context parameters
    llama_context_params ctx_params = llama_context_default_params();
    ctx_params.n_ctx = 2048;
    ctx_params.n_batch = 128;  // Reduced for better performance
    ctx_params.n_threads = 4;  // Fewer threads to reduce contention
    ctx_params.n_threads_batch = 4;  // Match decode threads

    // Create context
    g_ctx = llama_new_context_with_model(g_model, ctx_params);

    if (!g_ctx) {
        LOGE("Failed to create context");
        llama_free_model(g_model);
        g_model = nullptr;
        return JNI_FALSE;
    }

    // Create sampler for greedy decoding (deterministic)
    auto sparams = llama_sampler_chain_default_params();
    g_sampler = llama_sampler_chain_init(sparams);
    llama_sampler_chain_add(g_sampler, llama_sampler_init_greedy());

    LOGI("Model loaded successfully");
    return JNI_TRUE;
}

JNIEXPORT jstring JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeInference(
        JNIEnv* env, jobject thiz, jstring prompt) {

    if (!g_ctx || !g_model || !g_sampler) {
        LOGE("Model not initialized");
        return env->NewStringUTF("");
    }

    const char* prompt_text = env->GetStringUTFChars(prompt, nullptr);
    LOGI("Running inference, prompt: %s", prompt_text);

    // Format using Qwen3 chat template with /no_think to disable thinking mode
    // Qwen3 format: <|im_start|>system\n/no_think\nYou are Qwen.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n
    std::string formatted_prompt = "<|im_start|>system\n/no_think\nYou are Qwen.<|im_end|>\n<|im_start|>user\n";
    formatted_prompt += prompt_text;
    formatted_prompt += "<|im_end|>\n<|im_start|>assistant\n";

    env->ReleaseStringUTFChars(prompt, prompt_text);
    LOGI("Formatted prompt: %s", formatted_prompt.c_str());

    // Tokenize the formatted prompt
    std::vector<llama_token> tokens_list;
    tokens_list.resize(llama_n_ctx(g_ctx));

    const llama_vocab* vocab = llama_model_get_vocab(g_model);
    int n_tokens = llama_tokenize(
            vocab,
            formatted_prompt.c_str(),
            formatted_prompt.length(),
            tokens_list.data(),
            tokens_list.size(),
            true,  // add_special
            true   // parse_special
    );

    if (n_tokens < 0) {
        LOGE("Tokenization failed");
        return env->NewStringUTF("");
    }

    tokens_list.resize(n_tokens);
    LOGI("Tokenized to %d tokens", n_tokens);

    // Reset sampler for new generation
    llama_sampler_reset(g_sampler);

    // Process prompt tokens
    for (int i = 0; i < n_tokens; i += 512) {
        int batch_size = std::min(512, n_tokens - i);
        llama_batch batch = llama_batch_get_one(tokens_list.data() + i, batch_size);

        if (llama_decode(g_ctx, batch) != 0) {
            LOGE("Failed to decode prompt batch at position %d", i);
            return env->NewStringUTF("");
        }
    }

    LOGI("Prompt decoded, starting generation");

    // Generate response (max 20 tokens for testing)
    std::string response;
    int max_tokens = 20;  // Reduced for faster testing

    for (int i = 0; i < max_tokens; i++) {
        // Sample next token
        llama_token new_token = llama_sampler_sample(g_sampler, g_ctx, -1);

        // Check for end of generation
        if (llama_token_is_eog(vocab, new_token)) {
            LOGI("EOG token reached at step %d", i);
            break;
        }

        // Decode token to text
        char buf[256];
        int n = llama_token_to_piece(vocab, new_token, buf, sizeof(buf), 0, true);
        if (n > 0) {
            response.append(buf, n);
        }

        // Continue generation with single token
        llama_batch batch = llama_batch_get_one(&new_token, 1);
        if (llama_decode(g_ctx, batch) != 0) {
            LOGE("Failed to decode at generation step %d", i);
            break;
        }

        // Log progress every 10 tokens
        if (i % 10 == 0) {
            LOGI("Generated %d tokens so far", i);
        }
    }

    LOGI("Generation complete: %s", response.c_str());
    return env->NewStringUTF(response.c_str());
}

JNIEXPORT void JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeCleanup(
        JNIEnv* env, jobject thiz) {

    if (g_sampler) {
        llama_sampler_free(g_sampler);
        g_sampler = nullptr;
    }

    if (g_ctx) {
        llama_free(g_ctx);
        g_ctx = nullptr;
    }

    if (g_model) {
        llama_free_model(g_model);
        g_model = nullptr;
    }

    llama_backend_free();
    LOGI("Model cleaned up");
}

} // extern "C"
