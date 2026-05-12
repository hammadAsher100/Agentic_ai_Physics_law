from typing import List, Dict, Any
from cognitive_entity import CognitiveEntity
from config import MAX_DIALECTIC_ROUNDS
from rich.console import Console
from rich.panel import Panel

console = Console()


class DialecticRecord:
    """
    A log of everything said during the debate.
    This gets passed to the Arbitration Engine for final judgment.
    """
    def __init__(self):
        self.opening_statements: Dict[str, str] = {}   # node_id -> statement
        self.exchanges: List[Dict[str, str]] = []       # list of {challenger, defender, challenge, response}
        self.round_count: int = 0


def run_dialectic(entities: List[CognitiveEntity]) -> DialecticRecord:
    """
    Main entry point. Runs the full multi-round debate.
    Returns a complete record of everything that was said.
    """
    record = DialecticRecord()

    console.print(Panel(
        f"[bold cyan]INITIATING AUTONOMOUS ADVERSARIAL DIALECTIC[/bold cyan]\n"
        f"Participants: {len(entities)} Cognitive Entities\n"
        f"Max Rounds: {MAX_DIALECTIC_ROUNDS}",
        title="DIALECTIC ENGINE"
    ))

    # ---- PHASE 1: Opening Statements ----
    console.print("\n[bold yellow]PHASE 1: Opening Statements[/bold yellow]")
    for entity in entities:
        console.print(f"\n[cyan]► {entity.node_id} stating position...[/cyan]")
        statement = entity.get_initial_statement()
        record.opening_statements[entity.node_id] = statement
        console.print(f"[dim]{statement[:200]}...[/dim]")  # Preview first 200 chars

    # ---- PHASE 2: Adversarial Cross-Examination ----
    for round_num in range(1, MAX_DIALECTIC_ROUNDS + 1):
        console.print(f"\n[bold yellow]PHASE 2 — Round {round_num}: Cross-Examination[/bold yellow]")
        record.round_count = round_num

        # Each entity challenges every other entity
        for challenger in entities:
            for defender in entities:
                if challenger.node_id == defender.node_id:
                    continue  # An entity doesn't challenge itself

                # Get the defender's current position (latest statement)
                # On round 1, we use opening statements
                # On later rounds, we use their last response
                if round_num == 1:
                    defender_position = record.opening_statements[defender.node_id]
                else:
                    # Find the defender's most recent response in the record
                    defender_position = _get_last_response(record, defender.node_id)

                console.print(
                    f"\n[blue]{challenger.node_id}[/blue] challenges "
                    f"[red]{defender.node_id}[/red]..."
                )

                # Challenger generates a challenge
                challenge = challenger.challenge_entity(
                    other_statement=defender_position,
                    other_id=defender.node_id
                )

                # Defender responds to the challenge
                response = defender.respond_to_challenge(
                    challenge=challenge,
                    challenger_id=challenger.node_id
                )

                # Log the exchange
                record.exchanges.append({
                    "round": round_num,
                    "challenger_id": challenger.node_id,
                    "defender_id": defender.node_id,
                    "challenge": challenge,
                    "response": response
                })

                console.print(f"  [dim]Challenge: {challenge[:120]}...[/dim]")
                console.print(f"  [dim]Response:  {response[:120]}...[/dim]")

    console.print(Panel(
        f"[green]Dialectic complete.[/green] {len(record.exchanges)} exchanges recorded.",
        title="DIALECTIC ENGINE — TERMINATED"
    ))

    return record


def _get_last_response(record: DialecticRecord, node_id: str) -> str:
    """Helper: finds the most recent thing a specific node said."""
    # Search backwards through exchanges to find this node's last response
    for exchange in reversed(record.exchanges):
        if exchange["defender_id"] == node_id:
            return exchange["response"]
    # Fall back to opening statement if no responses yet
    return record.opening_statements.get(node_id, "No statement available.")