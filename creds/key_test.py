import os
import sys
# Temporarily add parent dir to path for ezblender imports if needed.
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
    # Simple chat completion test
    response = client.chat.completions.create(
        model="gpt-4o",  # Standard OpenAI model name
        messages=[{"role": "user", "content": "Hello, can you see me?"}],
        max_tokens=20
    )
    print("✅ Key is valid, response:", response.choices[0].message.content)
except Exception as e:
    print("❌ Key may be invalid or other error:", e)
