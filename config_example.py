# DeepSeek API Configuration
# You can switch between Official API or Local Deployment here

# === Option 1: DeepSeek Official API (Default) ===
API_CONFIG = {
    "api_key": "YOUR_DEEPSEEK_API_KEY",
    "base_url": "https://api.deepseek.com",
    "model_name": "deepseek-reasoner", # Note: You can also use "deepseek-chat"
    # If using "deepseek-chat", uncomment the extra_body line below to enable thinking mode:
#     "extra_body": {"thinking": {"type": "enabled"}}
}

# === Option 2: Local Deployment (e.g., vLLM, SGLang) ===
# This configuration works for most OpenAI-compatible local inference frameworks
# API_CONFIG = {
#     "api_key": "sk-test",
#     "base_url": "http://yourlocalserver/v1",
#     "model_name": "deepseek-v32",
#     "extra_body": {"chat_template_kwargs": {"thinking": True}}
# }
