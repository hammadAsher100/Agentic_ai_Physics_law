import sys
import json
import argparse

# Parse arguments EARLY to set mock mode before importing other modules
parser = argparse.ArgumentParser(description="Project Tartarus — Cognitive Arbitration Engine")
parser.add_argument("--mock", action="store_true", help="Use mock telemetry data (for testing)")
parser.add_argument("--save", type=str, default=None, help="Save result to a JSON file")
parser.add_argument("--pyc", type=str, default="tartarus_core.pyc", help="Path to the .pyc module")
args = parser.parse_args()

# Set mock mode in config BEFORE importing other modules
import config
config.MOCK_MODE = args.mock

# Now import the rest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our modules
from data_loader import load_tartarus_module, extract_telemetry, load_mock_telemetry
from cognitive_entity import CognitiveEntity
from dialectic_engine import run_dialectic
from arbitration_engine import run_arbitration

console = Console()


def main():
    # ---- Banner ----
    console.print(Panel(
        "[bold red]PROJECT TARTARUS[/bold red]\n"
        "[bold cyan]Cognitive Arbitration Engine — INITIALIZING[/bold cyan]\n"
        "Operational Authority: Cognitive Arbitration Command",
        title="[bold]* CLASSIFIED DIRECTIVE[/bold]"
    ))

    # ---- Step 1: Load Telemetry Data ----
    console.print("\n[bold]STEP 1: Loading Telemetry Data[/bold]")
    if args.mock:
        node_data_list = load_mock_telemetry()
    else:
        module = load_tartarus_module(args.pyc)
        node_data_list = extract_telemetry(module)

    if not node_data_list:
        console.print("[red]ERROR: No node data found. Aborting.[/red]")
        sys.exit(1)

    # ---- Step 2: Instantiate Cognitive Entities ----
    console.print(f"\n[bold]STEP 2: Instantiating {len(node_data_list)} Cognitive Entities[/bold]")
    entities = [CognitiveEntity(data) for data in node_data_list]

    # ---- Step 3: Run the Dialectic (the debate) ----
    console.print("\n[bold]STEP 3: Running Autonomous Adversarial Dialectic[/bold]")
    dialectic_record = run_dialectic(entities)

    # ---- Step 4: Run Arbitration (the final verdict) ----
    console.print("\n[bold]STEP 4: Running Cognitive Arbitration[/bold]")
    resolution = run_arbitration(entities, dialectic_record)

    # ---- Step 5: Display Results ----
    console.print("\n")
    console.print(Panel(
        "[bold green]RESOLUTION ACHIEVED[/bold green]",
        title="COGNITIVE ARBITRATION ENGINE — OUTPUT"
    ))

    # Show compromised nodes
    table = Table(title="Node Status")
    table.add_column("Node ID", style="cyan")
    table.add_column("Status", style="bold")

    all_ids = [e.node_id for e in entities]
    for node_id in all_ids:
        if node_id in resolution.compromised_node_ids:
            table.add_row(node_id, "[red]* COMPROMISED[/red]")
        else:
            table.add_row(node_id, "[green]+ VERIFIED[/green]")

    console.print(table)

    # Show the true reactor state
    console.print("\n[bold cyan]ABSOLUTE TRUTH STATE:[/bold cyan]")
    for key, value in resolution.absolute_truth_state.items():
        console.print(f"  {key}: [yellow]{value}[/yellow]")

    # Show physics reasoning
    console.print("\n[bold cyan]PHYSICS MATRIX:[/bold cyan]")
    console.print(f"  Invariants: {', '.join(resolution.physics_matrix.invariants_used)}")
    console.print(f"  Contradictions found: {len(resolution.physics_matrix.contradictions_found)}")
    for c in resolution.physics_matrix.contradictions_found:
        console.print(f"    • {c}")
    console.print(f"  Reasoning: {resolution.physics_matrix.reasoning_summary}")

    # Show confidence
    confidence_color = {"HIGH": "green", "MEDIUM": "yellow", "LOW": "red"}.get(
        resolution.confidence_level, "white"
    )
    console.print(
        f"\n  Confidence: [{confidence_color}]{resolution.confidence_level}[/{confidence_color}]"
        f" | Rounds: {resolution.dialectic_rounds_completed}"
    )

    # ---- Step 6: Save to file if requested ----
    final_json = resolution.model_dump()
    if args.save:
        with open(args.save, "w") as f:
            json.dump(final_json, f, indent=2)
        console.print(f"\n[green]+ Results saved to: {args.save}[/green]")
    else:
        console.print("\n[bold]FULL RESOLUTION JSON:[/bold]")
        console.print(json.dumps(final_json, indent=2))


if __name__ == "__main__":
    main()