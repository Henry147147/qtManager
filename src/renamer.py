from openai import OpenAI
# Configured by environment variables
client = OpenAI(base_url="http://localhost:8110/v1", api_key="")

messages = [
    {"role": "user", "content": "What are the most important rules when designing a new product?"},
]

chat_response = client.chat.completions.create(
    model="gemma-4-E4B-it",
    messages=messages,
    max_tokens=8192,
)
print("Chat response:", chat_response)
