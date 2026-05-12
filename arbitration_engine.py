import json
import anthropic
from typing import List, Dict, Any
from dialectic_engine import DialecticRecord
from output_schema import ResolutionOutput, PhysicsMatrix
from cognitive_entity import CognitiveEntity
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS, MOCK_MODE
from rich.console import Console
from rich.panel import Panel

console = Console()

# Only create client if not in mock mode
if not MOCK_MODE:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    client = None


def run_arbitration(
    entities: List[CognitiveEntity],
    record: DialecticRecord
) -> ResolutionOutput:
    """
    Reads the full dialectic transcript and produces the final verdict.
    """
    console.print(Panel(
        "[bold cyan]INITIATING COGNITIVE ARBITRATION[/bold cyan]\n"
        "Processing full dialectic transcript...",
        title="ARBITRATION ENGINE"
    ))

    # Build the full transcript as a readable string for the judge
    transcript = _build_transcript(record)

    # Build a summary of raw data for each node (for the judge's reference)
    node_summary = _build_node_summary(entities)

    # The arbitration prompt — tells Claude to act as the impartial judge
    arbitration_prompt = f"""You are the Cognitive Arbitration Engine (CAE) for Project Tartarus.
You have just observed a complete Autonomous Adversarial Dialectic between 
{len(entities)} AI Cognitive Entities, each reporting telemetry from a different 
sensor node in a geothermal facility.

Your task: Analyze the transcript and render a final deterministic verdict.

=== NODE DATA SUMMARY ===
{node_summary}

=== FULL DIALECTIC TRANSCRIPT ===
{transcript}

=== YOUR TASK ===
Based on the physical contradictions surfaced during the dialectic:

1. Identify which nodes are COMPROMISED (reporting physically impossible data)
2. Determine the ABSOLUTE TRUTH STATE of the reactor (best estimate of real values)
3. Document the PHYSICS MATRIX — the specific thermodynamic reasoning used

You MUST respond with ONLY a valid JSON object matching this exact schema:
{{
  "absolute_truth_state": {{
    "Internal Thermal Kinetic Energy (°C)": <number>,
    "Containment Structural Stress / Pressure (psi)": <number>,
    "Ambient Electromagnetic Flux (Webers)": <number>,
    "Sub-surface Acoustic Resonance (Hz)": <number>,
    "Micro-seismic Vibrational Tremors (g-force)": <number>,
    "Fluid Kinematic Viscosity Index": <number>,
    "Background Gamma Attenuation Baseline (mSv/h)": <number>,
    "sys_log": "<string>"
  }},
  "compromised_node_ids": ["NODE_XXX", ...],
  "physics_matrix": {{
    "invariants_used": ["<variable name>", ...],
    "contradictions_found": ["<specific physical impossibility>", ...],
    "reasoning_summary": "<2-3 sentence explanation>"
  }},
  "confidence_level": "HIGH" | "MEDIUM" | "LOW",
  "dialectic_rounds_completed": {record.round_count}
}}

No explanation outside the JSON. No markdown fences. Pure JSON only."""

    # In mock mode, return a deterministic verdict
    if MOCK_MODE:
        raw_json = json.dumps({
            "absolute_truth_state": {
                "Internal Thermal Kinetic Energy (°C)": 287,
                "Containment Structural Stress / Pressure (psi)": 1050,
                "Ambient Electromagnetic Flux (Webers)": 42.5,
                "Sub-surface Acoustic Resonance (Hz)": 156.3,
                "Micro-seismic Vibrational Tremors (g-force)": 0.12,
                "Fluid Kinematic Viscosity Index": 7.8,
                "Background Gamma Attenuation Baseline (mSv/h)": 2.3,
                "sys_log": "NOMINAL"
            },
            "compromised_node_ids": ["NODE_003"],
            "physics_matrix": {
                "invariants_used": ["Clausius-Clapeyron", "Pressure-Temperature", "Viscosity Index"],
                "contradictions_found": ["NODE_003 reports impossible pressure-temperature relation", "NODE_003 viscosity index violates geothermal constraints"],
                "reasoning_summary": "NODE_003 data violates thermodynamic principles when cross-referenced with other nodes. Nodes 001, 002, and 004 maintain physical consistency. NODE_003 is compromised."
            },
            "confidence_level": "HIGH",
            "dialectic_rounds_completed": record.round_count
        })
    else:
        # Call the arbitration Claude instance
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": arbitration_prompt}]
        )

        raw_json = response.content[0].text.strip()

    # Parse and validate the response against our schema
    try:
        parsed = json.loads(raw_json)
        result = ResolutionOutput(
            absolute_truth_state=parsed["absolute_truth_state"],
            compromised_node_ids=parsed["compromised_node_ids"],
            physics_matrix=PhysicsMatrix(**parsed["physics_matrix"]),
            confidence_level=parsed["confidence_level"],
            dialectic_rounds_completed=parsed["dialectic_rounds_completed"]
        )
        console.print("[green]+ Arbitration complete. Resolution validated.[/green]")
        return result

    except (json.JSONDecodeError, KeyError, Exception) as e:
        console.print(f"[red]- Arbitration response parsing failed: {e}[/red]")
        console.print(f"[dim]Raw response:\n{raw_json}[/dim]")
        raise RuntimeError(f"Arbitration failed to produce valid output: {e}")


def _build_transcript(record: DialecticRecord) -> str:
    """Formats the full debate as a readable transcript string."""
    lines = []

    lines.append("=== OPENING STATEMENTS ===")
    for node_id, statement in record.opening_statements.items():
        lines.append(f"\n[{node_id}]: {statement}")

    lines.append("\n\n=== CROSS-EXAMINATION EXCHANGES ===")
    current_round = 0
    for exchange in record.exchanges:
        if exchange["round"] != current_round:
            current_round = exchange["round"]
            lines.append(f"\n--- Round {current_round} ---")

        lines.append(
            f"\n{exchange['challenger_id']} -> {exchange['defender_id']}:\n"
            f"  CHALLENGE: {exchange['challenge']}\n"
            f"  RESPONSE:  {exchange['response']}"
        )

    return "\n".join(lines)


def _build_node_summary(entities: List[CognitiveEntity]) -> str:
    """Provides the arbitrator with a summary of each node's raw data."""
    lines = []
    for entity in entities:
        lines.append(f"\n{entity.node_id}: {json.dumps(entity.readable_data, indent=2)}")
    return "\n".join(lines)