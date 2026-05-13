"""Extract readable strings from the .pyc binary file."""
import re

with open('Tartarus_Core.pyc', 'rb') as f:
    raw = f.read()

print(f"File size: {len(raw)} bytes")
print(f"\n=== All printable ASCII strings (length >= 3) ===\n")

# Find all printable ASCII strings of length >= 3
strings = re.findall(rb'[\x20-\x7e]{3,}', raw)
for s in strings:
    print(s.decode('ascii', errors='replace'))

print(f"\n=== Looking for JSON-like patterns ===\n")
# Look for JSON-like dict patterns
json_patterns = re.findall(rb'\{[^}]*\}', raw)
for p in json_patterns:
    try:
        print(p.decode('utf-8'))
    except:
        pass
