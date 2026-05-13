"""Test different Gemini models to find one with available quota."""
import os
from pathlib import Path

for line in Path(".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Try different models
models_to_try = [
    "gemini-2.5-flash",
    "gemini-1.5-flash", 
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
]

for model_name in models_to_try:
    print(f"\nTesting: {model_name}...", end=" ")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Say hello in one word.",
            config=types.GenerateContentConfig(max_output_tokens=10),
        )
        print(f"SUCCESS -> {response.text.strip()}")
    except Exception as e:
        err = str(e)
        if "429" in err:
            print("RATE LIMITED (quota exhausted)")
        elif "404" in err:
            print("NOT FOUND")
        else:
            print(f"ERROR: {err[:80]}")
