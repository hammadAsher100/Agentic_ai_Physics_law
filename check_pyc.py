import struct, sys, importlib.util

# Check .pyc magic number
with open('Tartarus_Core.pyc', 'rb') as f:
    magic = f.read(4)
    print(f"PYC magic bytes: {magic.hex()}")
    print(f"PYC magic number: {struct.unpack('<H', magic[:2])[0]}")

# Current Python's magic number
print(f"Current Python magic: {importlib.util.MAGIC_NUMBER.hex()}")
print(f"Current Python version: {sys.version}")

# Try loading it
try:
    spec = importlib.util.spec_from_file_location("Tartarus_Core", "Tartarus_Core.pyc")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(f"\nModule loaded successfully!")
    print(f"Module attributes: {dir(module)}")
    if hasattr(module, 'get_telemetry_shards'):
        result = module.get_telemetry_shards()
        print(f"\nget_telemetry_shards() returned: {result}")
    else:
        print("\nWARNING: No get_telemetry_shards function found!")
        print("Available functions:", [x for x in dir(module) if not x.startswith('_')])
except Exception as e:
    print(f"\nFailed to load: {e}")
