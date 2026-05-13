"""Test gemini-2.5-flash specifically."""
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

print("Testing gemini-2.5-flash...")
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in exactly one word. No explanation.",
        config=types.GenerateContentConfig(max_output_tokens=50),
    )
    print(f"Response object: {response}")
    print(f"Response text: {repr(response.text)}")
    print(f"Candidates: {response.candidates}")
    print("\nSUCCESS! gemini-2.5-flash has available quota.")
except Exception as e:
    print(f"ERROR: {e}")
