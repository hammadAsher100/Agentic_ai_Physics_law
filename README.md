# Project Tartarus — Cognitive Arbitration Engine (CAE)

## What This Is

A multi-agent AI system that identifies compromised sensor nodes in a geothermal facility by having Claude instances debate each other using thermodynamic reasoning — no heuristics, no statistical models.

---

## Project Structure

```
tartarus_cae/
├── main.py               ← RUN THIS to start everything
├── config.py             ← Settings and key decryption map
├── data_loader.py        ← Reads from tartarus_core.pyc
├── cognitive_entity.py   ← One AI agent per node
├── dialectic_engine.py   ← Orchestrates the debate
├── arbitration_engine.py ← Final judge AI
├── output_schema.py      ← Defines the output JSON shape
├── requirements.txt      ← Python packages
├── .env.template         ← Copy to .env and add your API key
└── README.md             ← This file
```

---

## How the System Works (Plain English)

```
1. Load telemetry from tartarus_core.pyc
        ↓
2. Each node's JSON → one CognitiveEntity (Claude instance)
   Each entity knows ONLY its own data
        ↓
3. Entities give opening statements ("here's what I observe, it's consistent because...")
        ↓
4. Entities cross-examine each other ("your pressure reading is impossible given X because...")
        ↓
5. Defender responds ("I disagree / you're right, that's a contradiction")
        ↓
6. Arbitration Engine reads full transcript → renders final verdict
        ↓
7. Output: true reactor state + which nodes lied + the physics reasoning
```

---

## Setup (Do This First)

### 1. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
```bash
cp .env.template .env
# Open .env and paste your Anthropic API key
```

### 4. Place the .pyc file
Put `tartarus_core.pyc` in the same folder as `main.py`.

---

## Running the System

### Test with mock data (no .pyc needed):
```bash
python main.py --mock
```

### Run with the real module:
```bash
python main.py
```

### Save results to a file:
```bash
python main.py --save results.json
```

---

## When You Get the .pyc File

1. Put it in the project root folder
2. Open `data_loader.py`
3. Run this in a Python shell to see what functions are available:
   ```python
   import tartarus_core
   print(dir(tartarus_core))
   ```
4. Find the function that returns the telemetry data
5. Update the `extract_telemetry()` function in `data_loader.py` accordingly

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ANTHROPIC_API_KEY is not set` | You forgot to copy `.env.template` to `.env` |
| `Cannot find tartarus_core.pyc` | Put the .pyc file in the project root |
| `Function 'get_telemetry' not found` | Run `dir(tartarus_core)` and update `data_loader.py` |
| API rate limit errors | Reduce `MAX_DIALECTIC_ROUNDS` in `.env` |

---

## Output Format

```json
{
  "absolute_truth_state": {
    "Internal Thermal Kinetic Energy (°C)": 847.3,
    "Containment Structural Stress / Pressure (psi)": 2150.0,
    ...
  },
  "compromised_node_ids": ["NODE_003"],
  "physics_matrix": {
    "invariants_used": ["Temperature", "Pressure"],
    "contradictions_found": ["NODE_003 reports 200°C with 9999 psi — thermodynamically impossible"],
    "reasoning_summary": "..."
  },
  "confidence_level": "HIGH",
  "dialectic_rounds_completed": 3
}
```