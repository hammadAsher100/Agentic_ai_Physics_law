# ============================================================
# data_loader.py — Reads telemetry data from tartarus_core.pyc
# ============================================================
# This module is the bridge between the encrypted data module
# (provided by your professor) and the rest of our system.
#
# HOW IT WORKS:
# - tartarus_core.pyc is a compiled Python file. Python can import it
#   directly even though you can't read its source code.
# - We call functions from it to retrieve the telemetry JSON strings.
# - Each JSON string becomes one "Node's data".
#
# NOTE: We don't know the exact function names yet (you'll get the
# .pyc file later). This module is designed to be easily updated
# once you have it. Look for the TODO comments.

import json
import importlib
import sys
import os
from typing import List, Dict, Any
from rich.console import Console

console = Console()


def load_tartarus_module(pyc_path: str = "tartarus_core.pyc"):
    """
    Dynamically imports the compiled tartarus_core module.
    Place the .pyc file in the same folder as this script.
    """
    if not os.path.exists(pyc_path):
        raise FileNotFoundError(
            f"Cannot find '{pyc_path}'. "
            "Place the tartarus_core.pyc file in the project root directory."
        )

    # Add the directory containing the .pyc to Python's module search path
    module_dir = os.path.dirname(os.path.abspath(pyc_path))
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    # Import the compiled module
    module_name = os.path.splitext(os.path.basename(pyc_path))[0]
    module = importlib.import_module(module_name)
    console.print(f"[green]+ Loaded module:[/green] {module_name}")
    return module


def extract_telemetry(module) -> List[Dict[str, Any]]:
    """
    Calls the tartarus_core module to retrieve all node telemetry.
    Returns a list of dicts, one per node.

    TODO: Once you have the .pyc file, run this to see what's inside:
        import tartarus_core
        print(dir(tartarus_core))
    Then update the function call below to match the actual function name.
    """

    # ---- UPDATE THIS SECTION WHEN YOU GET THE .pyc FILE ----
    # Common patterns professors use — try these one by one:
    #
    # Option A: module.get_telemetry()
    # Option B: module.retrieve_data()
    # Option C: module.get_nodes()
    # Option D: module.load()
    #
    # For now, we use a placeholder that lets us test without the file:

    try:
        # Try the most likely function name first
        raw_data = module.get_telemetry()
    except AttributeError:
        # If that fails, list what IS available and let the user know
        available = [x for x in dir(module) if not x.startswith("_")]
        raise AttributeError(
            f"Function 'get_telemetry()' not found in tartarus_core.\n"
            f"Available functions/attributes: {available}\n"
            f"Update data_loader.py with the correct function name."
        )
    # ---------------------------------------------------------

    # The raw data might be a list of JSON strings or a list of dicts
    nodes = []
    for i, item in enumerate(raw_data):
        if isinstance(item, str):
            # Parse JSON string into a dict
            node_data = json.loads(item)
        elif isinstance(item, dict):
            node_data = item
        else:
            console.print(f"[yellow]Warning: Node {i} has unexpected type {type(item)}, skipping[/yellow]")
            continue

        # Ensure every node has an ID
        if "node_id" not in node_data:
            node_data["node_id"] = f"NODE_{i:03d}"

        nodes.append(node_data)
        console.print(f"[cyan]  Loaded Node:[/cyan] {node_data['node_id']}")

    console.print(f"\n[green]+ Total nodes loaded:[/green] {len(nodes)}")
    return nodes


# ============================================================
# MOCK DATA — Used for testing BEFORE you get the .pyc file
# ============================================================
# This simulates what the real data might look like.
# Delete or comment this out once you have the real module.

MOCK_TELEMETRY = [
    {
        "node_id": "NODE_001",
        "v_m1": 847.3,   # Temperature °C
        "v_m2": 2150.0,  # Pressure psi
        "v_m3": 0.042,   # EM Flux
        "v_m4": 12.7,    # Acoustic Hz
        "v_m5": 0.003,   # Seismic g-force
        "v_m6": 1.82,    # Viscosity
        "v_m7": 0.15,    # Gamma mSv/h
        "sys_log": "NOMINAL — all containment parameters within expected range"
    },
    {
        "node_id": "NODE_002",
        "v_m1": 849.1,
        "v_m2": 2148.5,
        "v_m3": 0.041,
        "v_m4": 12.9,
        "v_m5": 0.004,
        "v_m6": 1.80,
        "v_m7": 0.14,
        "sys_log": "NOMINAL — standard geothermal cycle active"
    },
    {
        "node_id": "NODE_003",  # <-- This one is "compromised"
        "v_m1": 200.0,   # Impossibly low temp given the pressure
        "v_m2": 9999.9,  # Impossibly high pressure
        "v_m3": 15.7,    # Wildly different EM flux
        "v_m4": 0.1,
        "v_m5": 2.8,     # Very high seismic
        "v_m6": 0.01,
        "v_m7": 88.0,    # Impossibly high gamma
        "sys_log": "CRITICAL ERROR — cascading containment failure imminent"
    },
    {
        "node_id": "NODE_004",
        "v_m1": 846.8,
        "v_m2": 2152.0,
        "v_m3": 0.043,
        "v_m4": 12.6,
        "v_m5": 0.003,
        "v_m6": 1.83,
        "v_m7": 0.16,
        "sys_log": "NOMINAL — coolant flow stable"
    },
]


def load_mock_telemetry() -> List[Dict[str, Any]]:
    """Use this for testing before the real .pyc is available."""
    console.print("[yellow]* Using MOCK telemetry data (for testing only)[/yellow]")
    return MOCK_TELEMETRY