./llama.cpp/llama-server \
    --model models/gemma-4-E4B-it-UD-Q8_K_XL.gguf \
    --temp 1.0 \
    --top-p 0.95 \
    --top-k 64 \
    --alias "gemma-4-E4B-it" \
    --port 8110 \
    --chat-template-kwargs '{"enable_thinking":true}'