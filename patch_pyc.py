"""
Patch Tartarus_Core.pyc magic number from Python 3.12 to Python 3.13
so it can be imported in the current environment.
"""
import importlib.util
import struct

INPUT = 'Tartarus_Core.pyc'
OUTPUT = 'Tartarus_Core_patched.pyc'

# Read original file
with open(INPUT, 'rb') as f:
    data = bytearray(f.read())

old_magic = data[:4]
print(f"Original magic: {old_magic.hex()} (Python 3.12)")

# Get current Python's magic number
new_magic = importlib.util.MAGIC_NUMBER
print(f"Target magic:   {new_magic.hex()} (Python 3.13)")

# Patch the magic number
data[:4] = new_magic

# Write patched file
with open(OUTPUT, 'wb') as f:
    f.write(data)

print(f"\nPatched file written to: {OUTPUT}")

# Try importing the patched file
print("\n=== Testing import of patched file ===")
try:
    spec = importlib.util.spec_from_file_location("Tartarus_Core", OUTPUT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("SUCCESS! Module loaded.")
    
    if hasattr(module, 'get_telemetry_shards'):
        result = module.get_telemetry_shards()
        print(f"\nget_telemetry_shards() returned {len(result)} items:")
        import json
        for item in result:
            if isinstance(item, str):
                print(json.dumps(json.loads(item), indent=2))
            else:
                print(json.dumps(item, indent=2))
    else:
        print(f"Available attrs: {[a for a in dir(module) if not a.startswith('_')]}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
