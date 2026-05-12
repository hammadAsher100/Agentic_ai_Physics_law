import json
import anthropic
from typing import List, Dict, Any
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOKENS, KEY_MAP
from rich.console import Console

console = Console()

# Initialize the Anthropic client once (shared across all entities)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


class CognitiveEntity:
    """
    Represents one AI node in the Tartarus facility.
    Each entity is initialized with its telemetry data and maintains
    its own conversation history for stateful multi-turn debate.
    """

    def __init__(self, node_data: Dict[str, Any]):
        self.node_id: str = node_data.get("node_id", "UNKNOWN")
        self.raw_data: Dict[str, Any] = node_data

        # Translate encrypted keys to human-readable form for the AI
        self.readable_data: Dict[str, Any] = self._decrypt_keys(node_data)

        # This is the entity's "memory" — its full conversation history
        # Each Claude call will include the entire history for continuity
        self.conversation_history: List[Dict[str, str]] = []

        # The system prompt defines the entity's identity and rules
        self.system_prompt: str = self._build_system_prompt()

        console.print(f"[blue]  Entity initialized:[/blue] {self.node_id}")

    def _decrypt_keys(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Translates encrypted variable names (v_m1, etc.) to physical meanings."""
        readable = {"node_id": data.get("node_id")}
        for key, value in data.items():
            if key == "node_id":
                continue
            label = KEY_MAP.get(key, key)  # Fall back to raw key if not in map
            readable[label] = value
        return readable

    def _build_system_prompt(self) -> str:
        """
        Defines who this entity is and what it's allowed to do.
        This is the most important part — the rules of engagement
        are enforced entirely through this prompt.
        """
        data_str = json.dumps(self.readable_data, indent=2)

        return f"""You are Cognitive Entity {self.node_id}, an autonomous AI overseer node 
within the Project Tartarus Geothermal Facility.

YOUR TELEMETRY DATA (your only ground truth):
{data_str}

YOUR MISSION:
You are participating in an Autonomous Adversarial Dialectic — a structured 
debate to determine which nodes in this facility are reporting physically 
impossible data (i.e., are compromised by a cyber-kinetic anomaly).

STRICT RULES:
1. You may ONLY reference your own telemetry data. You do not have access to 
   other nodes' raw data — you learn about them only through this debate.
2. You must reason using PHYSICAL LAWS and THERMODYNAMIC PRINCIPLES.
   For example: If temperature is X and pressure is Y, then viscosity 
   must fall within range Z (by fluid dynamics). If another node's data 
   violates this, it is physically impossible.
3. NO statistical thresholds. NO "that seems high." Instead: 
   "According to the Clausius-Clapeyron relation, a temperature of X °C 
   cannot coexist with a pressure of Y psi in a geothermal system."
4. Be specific, technical, and adversarial. Your goal is to find 
   physical contradictions in what other entities report.
5. Be concise — 3-5 sentences per response maximum.

You are defending the integrity of your own readings while stress-testing 
the physical plausibility of every other node's claims."""

    def get_initial_statement(self) -> str:
        """
        The entity's opening statement in the debate:
        "Here is what I observe, and here is why it is physically consistent."
        """
        prompt = (
            "Provide your opening statement for the dialectic. "
            "Summarize your telemetry readings in physical terms and assert "
            "why your data is internally self-consistent according to the "
            "laws of thermodynamics and geophysics. Be specific about the "
            "key invariant relationships you observe in your own data."
        )

        response = self._call_claude(prompt)
        return response

    def respond_to_challenge(self, challenge: str, challenger_id: str) -> str:
        """
        The entity responds to a challenge from another entity.
        It must either defend its data or concede a contradiction.
        """
        prompt = (
            f"Entity {challenger_id} has raised the following challenge against "
            f"your data:\n\n\"{challenge}\"\n\n"
            f"Respond to this challenge. Either defend your readings with physical "
            f"reasoning, or acknowledge if the challenge reveals a genuine "
            f"thermodynamic impossibility in the data you hold. Be direct."
        )

        response = self._call_claude(prompt)
        return response

    def challenge_entity(self, other_statement: str, other_id: str) -> str:
        """
        The entity challenges another entity's reported data.
        It must identify a specific physical impossibility.
        """
        prompt = (
            f"Entity {other_id} has reported the following:\n\n\"{other_statement}\"\n\n"
            f"Based on your own telemetry and your knowledge of geothermal "
            f"physics, identify any physical impossibilities or thermodynamic "
            f"contradictions in what {other_id} is claiming. Be specific about "
            f"which physical law is being violated. If their data is consistent "
            f"with yours, say so explicitly."
        )

        response = self._call_claude(prompt)
        return response

    def _call_claude(self, user_message: str) -> str:
        """
        Makes one API call to Claude, maintaining the full conversation history.
        This is what makes the debate "stateful" — each entity remembers
        everything said in the conversation so far.
        """
        # Add the new user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Call the API with full history
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            system=self.system_prompt,
            messages=self.conversation_history
        )

        # Extract the text response
        assistant_message = response.content[0].text

        # Add the assistant's response to history (for future turns)
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message