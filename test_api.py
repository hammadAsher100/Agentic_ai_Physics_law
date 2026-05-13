"""Quick API key test - minimal request to check if key works."""
import os
from pathlib import Path

# Load .env
for line in Path(".env").read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()

from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY", "")
print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Say hello in one word.",
        config=types.GenerateContentConfig(max_output_tokens=10),
    )
    print(f"SUCCESS: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
    
    # Try listing available models to verify key is valid
    print("\nTrying to list models to verify key validity...")
    try:
        for m in client.models.list():
            if "flash" in m.name.lower():
                print(f"  Available: {m.name}")
                break
        print("Key is VALID but rate-limited. Wait a few minutes and retry.")
    except Exception as e2:
        print(f"Key validation failed: {e2}")
        print("The API key may be INVALID or disabled.")
