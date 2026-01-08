#include <jni.h>
#include <android/log.h>
#include <string>
#include <vector>
#include <cstring>
#include <chrono>

// Include llama.cpp headers
#include "llama.h"
#include "sampling.h"

#define LOG_TAG "LlamaJNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// Performance metrics logging
#define PERF_TAG "LlamaPerf"
#define LOGP(...) __android_log_print(ANDROID_LOG_INFO, PERF_TAG, __VA_ARGS__)

// High-resolution timing helper
using Clock = std::chrono::high_resolution_clock;
using TimePoint = std::chrono::time_point<Clock>;

inline double elapsed_ms(TimePoint start, TimePoint end) {
    return std::chrono::duration<double, std::milli>(end - start).count();
}

// Global model and context
static llama_model* g_model = nullptr;
static llama_context* g_ctx = nullptr;
static llama_sampler* g_sampler = nullptr;

// System prompt caching state
static int g_system_prompt_tokens = 0;      // Number of tokens in cached system prompt
static bool g_system_prompt_cached = false; // Whether system prompt is in KV cache

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

JNIEXPORT jint JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeCacheSystemPrompt(
        JNIEnv* env, jobject thiz, jstring system_prompt) {

    if (!g_ctx || !g_model) {
        LOGE("Model not initialized, cannot cache system prompt");
        return -1;
    }

    const char* prompt_text = env->GetStringUTFChars(system_prompt, nullptr);
    std::string system_str = prompt_text;
    env->ReleaseStringUTFChars(system_prompt, prompt_text);

    LOGI("Caching system prompt (%zu chars)...", system_str.length());

    // Clear any existing KV cache
    llama_memory_clear(llama_get_memory(g_ctx), true);
    g_system_prompt_cached = false;
    g_system_prompt_tokens = 0;

    // Tokenize system prompt
    std::vector<llama_token> tokens_list;
    tokens_list.resize(llama_n_ctx(g_ctx));

    const llama_vocab* vocab = llama_model_get_vocab(g_model);
    int n_tokens = llama_tokenize(
            vocab,
            system_str.c_str(),
            system_str.length(),
            tokens_list.data(),
            tokens_list.size(),
            true,  // add_special
            true   // parse_special
    );

    if (n_tokens < 0) {
        LOGE("Failed to tokenize system prompt");
        return -1;
    }

    tokens_list.resize(n_tokens);
    LOGI("System prompt tokenized to %d tokens", n_tokens);

    TimePoint t_start = Clock::now();

    // Process system prompt tokens (prefill)
    const int n_batch = 128;
    for (int i = 0; i < n_tokens; i += n_batch) {
        int batch_size = std::min(n_batch, n_tokens - i);
        llama_batch batch = llama_batch_get_one(tokens_list.data() + i, batch_size);

        if (llama_decode(g_ctx, batch) != 0) {
            LOGE("Failed to decode system prompt batch at position %d", i);
            return -1;
        }
    }

    TimePoint t_end = Clock::now();
    double prefill_ms = elapsed_ms(t_start, t_end);

    g_system_prompt_tokens = n_tokens;
    g_system_prompt_cached = true;

    LOGP("=== SYSTEM PROMPT CACHED: %d tokens in %.1f ms (%.1f tok/s) ===",
         n_tokens, prefill_ms, (n_tokens / prefill_ms) * 1000.0);

    return n_tokens;
}

JNIEXPORT void JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeInvalidateCache(
        JNIEnv* env, jobject thiz) {

    LOGI("Invalidating system prompt cache");
    g_system_prompt_cached = false;
    g_system_prompt_tokens = 0;

    if (g_ctx) {
        llama_memory_clear(llama_get_memory(g_ctx), true);
    }
}

JNIEXPORT jboolean JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeIsCacheValid(
        JNIEnv* env, jobject thiz) {
    return g_system_prompt_cached ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jstring JNICALL
Java_com_notifai_domain_classifier_LlamaClassifier_nativeInference(
        JNIEnv* env, jobject thiz, jstring prompt) {

    if (!g_ctx || !g_model || !g_sampler) {
        LOGE("Model not initialized");
        return env->NewStringUTF("");
    }

    const char* prompt_text = env->GetStringUTFChars(prompt, nullptr);
    std::string input_prompt = prompt_text;
    env->ReleaseStringUTFChars(prompt, prompt_text);

    const llama_vocab* vocab = llama_model_get_vocab(g_model);
    llama_memory_t kv = llama_get_memory(g_ctx);

    std::vector<llama_token> tokens_list;
    tokens_list.resize(llama_n_ctx(g_ctx));
    int n_tokens = 0;
    int prefill_start_pos = 0;

    if (g_system_prompt_cached && g_system_prompt_tokens > 0) {
        // FAST PATH: System prompt is cached in KV cache
        // Only need to clear tokens after system prompt and process user message
        LOGI("Using cached system prompt (%d tokens), processing user message only...",
             g_system_prompt_tokens);

        // Clear KV cache from system prompt position onwards (keep system prompt)
        llama_memory_seq_rm(kv, 0, g_system_prompt_tokens, -1);

        // Tokenize only the user message (don't add BOS since it's continuation)
        n_tokens = llama_tokenize(
                vocab,
                input_prompt.c_str(),
                input_prompt.length(),
                tokens_list.data(),
                tokens_list.size(),
                false,  // add_special = false (no BOS, continuing from system prompt)
                true    // parse_special
        );

        prefill_start_pos = g_system_prompt_tokens;

    } else {
        // SLOW PATH: No cache, process full prompt
        LOGI("No system prompt cache, processing full prompt...");

        // Clear entire KV cache
        llama_memory_clear(kv, true);

        // Tokenize the full prompt
        n_tokens = llama_tokenize(
                vocab,
                input_prompt.c_str(),
                input_prompt.length(),
                tokens_list.data(),
                tokens_list.size(),
                true,  // add_special
                true   // parse_special
        );

        prefill_start_pos = 0;
    }

    if (n_tokens < 0) {
        LOGE("Tokenization failed");
        return env->NewStringUTF("");
    }

    tokens_list.resize(n_tokens);
    LOGI("Tokenized to %d tokens (prefill start: %d)", n_tokens, prefill_start_pos);

    // Reset sampler for new generation
    llama_sampler_reset(g_sampler);

    // ===== PERFORMANCE TIMING START =====
    TimePoint t_start_total = Clock::now();
    TimePoint t_start_prefill = Clock::now();

    // Process prompt tokens (prefill phase)
    // When using cached system prompt, we need to set positions explicitly
    const int n_batch = 128;

    // Create batch with explicit positions for proper KV cache handling
    llama_batch batch = llama_batch_init(n_batch, 0, 1);

    for (int i = 0; i < n_tokens; i += n_batch) {
        int batch_size = std::min(n_batch, n_tokens - i);

        // Clear batch for reuse
        batch.n_tokens = 0;

        for (int j = 0; j < batch_size; j++) {
            int token_idx = i + j;
            int pos = prefill_start_pos + token_idx;  // Position in full context

            batch.token[batch.n_tokens] = tokens_list[token_idx];
            batch.pos[batch.n_tokens] = pos;
            batch.n_seq_id[batch.n_tokens] = 1;
            batch.seq_id[batch.n_tokens][0] = 0;
            batch.logits[batch.n_tokens] = (token_idx == n_tokens - 1);  // Only last token needs logits
            batch.n_tokens++;
        }

        if (llama_decode(g_ctx, batch) != 0) {
            LOGE("Failed to decode prompt batch at position %d", i);
            llama_batch_free(batch);
            return env->NewStringUTF("");
        }
    }

    llama_batch_free(batch);

    TimePoint t_end_prefill = Clock::now();
    double prefill_ms = elapsed_ms(t_start_prefill, t_end_prefill);
    double prefill_tps = (n_tokens / prefill_ms) * 1000.0;
    LOGP("=== PREFILL: %d tokens in %.1f ms (%.1f tok/s) [start_pos=%d] ===",
         n_tokens, prefill_ms, prefill_tps, prefill_start_pos);

    LOGI("Prompt decoded, starting generation");

    // Generate response (max 50 tokens for JSON output)
    std::string response;
    int max_tokens = 50;
    int tokens_generated = 0;
    TimePoint t_first_token;
    TimePoint t_start_decode = Clock::now();

    for (int i = 0; i < max_tokens; i++) {
        // Sample next token
        llama_token new_token = llama_sampler_sample(g_sampler, g_ctx, -1);

        // Record time to first token
        if (i == 0) {
            t_first_token = Clock::now();
            double ttft = elapsed_ms(t_start_total, t_first_token);
            LOGP("=== TIME TO FIRST TOKEN: %.1f ms ===", ttft);
        }

        // Check for end of generation
        if (llama_token_is_eog(vocab, new_token)) {
            LOGI("EOG token reached at step %d", i);
            break;
        }

        tokens_generated++;

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
    }

    TimePoint t_end_total = Clock::now();
    double total_ms = elapsed_ms(t_start_total, t_end_total);
    double decode_ms = elapsed_ms(t_start_decode, t_end_total);
    double decode_tps = tokens_generated > 0 ? (tokens_generated / decode_ms) * 1000.0 : 0;

    LOGP("=== DECODE: %d tokens in %.1f ms (%.2f tok/s) ===", tokens_generated, decode_ms, decode_tps);
    LOGP("=== TOTAL: %.1f ms | Prefill: %.1f ms | Decode: %.1f ms ===", total_ms, prefill_ms, decode_ms);
    LOGP("=== PERFORMANCE SUMMARY: TTFT=%.0fms, Decode=%.2f tok/s ===",
         elapsed_ms(t_start_total, t_first_token), decode_tps);

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
