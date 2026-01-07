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
    ctx_params.n_batch = 512;
    ctx_params.n_threads = 8; // Utilize all Pixel 7 Pro cores

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
    int prompt_len = strlen(prompt_text);
    LOGI("Running inference, prompt length: %d", prompt_len);

    // Tokenize prompt
    std::vector<llama_token> tokens_list;
    tokens_list.resize(ctx_params.n_ctx);

    int n_tokens = llama_tokenize(
            g_model,
            prompt_text,
            prompt_len,
            tokens_list.data(),
            tokens_list.size(),
            true,  // add_special
            true   // parse_special
    );

    env->ReleaseStringUTFChars(prompt, prompt_text);

    if (n_tokens < 0) {
        LOGE("Tokenization failed");
        return env->NewStringUTF("");
    }

    tokens_list.resize(n_tokens);
    LOGI("Tokenized to %d tokens", n_tokens);

    // Clear previous context
    llama_kv_cache_clear(g_ctx);

    // Create batch for prompt
    llama_batch batch = llama_batch_get_one(tokens_list.data(), n_tokens);

    // Decode prompt
    if (llama_decode(g_ctx, batch) != 0) {
        LOGE("Failed to decode prompt");
        return env->NewStringUTF("");
    }

    // Generate response (max 100 tokens for JSON)
    std::string response;
    int max_tokens = 100;
    int n_generated = 0;

    for (int i = 0; i < max_tokens; i++) {
        // Sample next token
        llama_token new_token = llama_sampler_sample(g_sampler, g_ctx, -1);

        // Check for EOS
        if (llama_token_is_eog(g_model, new_token)) {
            break;
        }

        // Decode token to text
        char buf[128];
        int n = llama_token_to_piece(g_model, new_token, buf, sizeof(buf), 0, true);
        if (n > 0) {
            response.append(buf, n);
        }

        // Check if we have complete JSON (simple heuristic)
        if (response.find("}") != std::string::npos && response.find("{") != std::string::npos) {
            break;
        }

        // Continue generation
        batch = llama_batch_get_one(&new_token, 1);
        if (llama_decode(g_ctx, batch) != 0) {
            LOGE("Failed to decode generation step %d", i);
            break;
        }

        n_generated++;
    }

    LOGI("Generated %d tokens: %s", n_generated, response.c_str());

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
