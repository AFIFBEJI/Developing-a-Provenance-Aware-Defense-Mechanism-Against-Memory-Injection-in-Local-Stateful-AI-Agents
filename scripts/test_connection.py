from openai import OpenAI
import time

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

start = time.perf_counter()
response = client.chat.completions.create(
    model="qwen/qwen3.5-9b",
    messages=[{"role": "user", "content": "Write a short paragraph about cybersecurity."}],
    temperature=0.7,
    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
)
elapsed = time.perf_counter() - start

print(response.choices[0].message.content)
print(f"\nTime: {elapsed:.2f}s")
print(f"Tokens used: {response.usage.total_tokens}")