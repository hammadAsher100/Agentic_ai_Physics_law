"""Extract code object from .pyc file, bypassing magic number check."""
import marshal
import dis
import types

with open('Tartarus_Core.pyc', 'rb') as f:
    # Skip header: 4 bytes magic + 4 bytes flags + 8 bytes timestamp/size (Python 3.12 format)
    header = f.read(16)
    print(f"Header (hex): {header.hex()}")
    
    # Read the marshalled code object
    code = marshal.load(f)

print(f"\nCode object loaded: {code}")
print(f"Co_consts: {code.co_consts}")
print(f"\nDisassembly:")
dis.dis(code)

# Look through all nested code objects for data
print("\n\n=== Searching all constants for data ===")
def find_data(code_obj, depth=0):
    prefix = "  " * depth
    for const in code_obj.co_consts:
        if isinstance(const, types.CodeType):
            print(f"{prefix}Found nested code object: {const.co_name}")
            find_data(const, depth + 1)
        elif isinstance(const, (dict, list, tuple)):
            print(f"{prefix}Found {type(const).__name__}: {const}")
        elif isinstance(const, str) and len(const) > 20:
            print(f"{prefix}Found string: {const[:100]}...")
        elif isinstance(const, (int, float)):
            print(f"{prefix}Found number: {const}")

find_data(code)

# Try to actually execute the code in a sandboxed namespace
print("\n\n=== Attempting execution ===")
namespace = {}
try:
    exec(code, namespace)
    print("Execution successful!")
    print(f"Namespace keys: {[k for k in namespace.keys() if not k.startswith('__')]}")
    if 'get_telemetry_shards' in namespace:
        result = namespace['get_telemetry_shards']()
        print(f"\nget_telemetry_shards() returned:")
        import json
        print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Execution failed: {e}")
