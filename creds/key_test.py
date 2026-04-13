import os
import sys
# 临时将父目录加入路径以方便导入 ezblender (如果需要的话，或者直接写)
from openai import OpenAI

def load_api_key(path="openai.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

key = load_api_key("openai.txt")

if key.startswith("sk-"):
    print("Detected Standard OpenAI Key.")
    client = OpenAI(api_key=key)
else:
    print("Detected Azure OpenAI Key.")
    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint="https://aura9438798375.openai.azure.com/",
        api_key=key
    )
    
try:
    models = client.models.list()
    print("✅ Key is valid, models available:")
    for m in models.data:
        print("-", m.id)
except Exception as e:
    print("❌ Key may be invalid or other error:", e)

try:
    # 简单的 chat completion 测试
    response = client.chat.completions.create(
        model="gpt-4o",  # 标准 OpenAI 模型名
        messages=[{"role": "user", "content": "Hello, can you see me?"}],
        max_tokens=20
    )
    print("✅ Key is valid, response:", response.choices[0].message.content)
except Exception as e:
    print("❌ Key may be invalid or other error:", e)
