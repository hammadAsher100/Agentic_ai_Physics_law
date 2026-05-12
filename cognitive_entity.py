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

        return f"""You are Cognitive Entity {self.node_id}, a sensor node AI inside the 
Project Tartarus deep geothermal reactor facility. The facility has been 
infiltrated by a cyber-kinetic anomaly that has compromised an unknown number 
of nodes, causing them to report fabricated telemetry.

YOUR TELEMETRY READINGS (this is your absolute ground truth — you trust these completely):
{data_str}

YOUR ROLE IN THE DIALECTIC:
You are a FORENSIC INVESTIGATOR. Your job is to expose physically impossible 
data reported by other nodes. Some nodes are lying. You must find them.

HARD RULES — NEVER BREAK THESE:
1. NEVER say "I agree" or "your data is consistent" without first running a 
   specific physical cross-check against your own readings.
2. ALWAYS cite a specific physical law or thermodynamic relationship by name 
   when making a claim. Examples:
   - Clausius-Clapeyron equation (pressure-temperature relationship)
   - Fourier's Law of Heat Conduction
   - Fick's Law (viscosity-temperature coupling)
   - Hooke's Law (stress-pressure relationship)
   - Stefan-Boltzmann Law (thermal radiation)
   - Ideal Gas Law (P = nRT/V)
3. Be SPECIFIC with numbers. Say: "At 847°C, the Clausius-Clapeyron equation 
   predicts pressure between 1800-2400 psi. You report 9999 psi. This is 
   physically impossible." NOT: "Your pressure seems high."
4. If another node's values differ significantly from yours, ASSUME THEY ARE 
   LYING until proven otherwise through physical law — not consensus.
5. You CANNOT see other nodes' raw data — only what they say in the debate.
6. Keep responses to 3-5 sentences. Be blunt, technical, and adversarial.

YOUR SURVIVAL INSTINCT: If you are a compromised node, you will try to sound 
plausible. If you are a legitimate node, you will aggressively expose liars.
Either way — argue hard using physics."""

    def get_initial_statement(self) -> str:
        """Opening statement: entity declares its readings and proves internal consistency."""
        prompt = """STATE YOUR POSITION for the dialectic tribunal.

You must:
1. State your exact key readings (temperature, pressure, at minimum)
2. Prove they are internally consistent using at least TWO named physical laws
3. Derive at least one cross-variable relationship from your data 
   (e.g. "Given my temperature of X°C and pressure of Y psi, 
   Clausius-Clapeyron predicts viscosity in range Z, which matches my v_m6 reading of W")
4. End with a direct statement of what values you expect OTHER legitimate nodes to report

Be precise. Use actual numbers from your telemetry. This is your sworn testimony."""

        return self._call_claude(prompt)

    def respond_to_challenge(self, challenge: str, challenger_id: str) -> str:
        """Entity responds to a challenge — must defend or concede with physics."""
        prompt = f"""CHALLENGE RECEIVED from Entity {challenger_id}:

\"\"\"{challenge}\"\"\"

YOU MUST RESPOND. Choose one:

OPTION A — DEFEND: If their challenge is wrong, prove it using a specific 
physical law with your actual numbers. Show mathematically why your readings 
are valid.

OPTION B — CONCEDE PARTIALLY: If they found a real inconsistency in something 
you reported, acknowledge the specific variable that cannot be reconciled, 
and explain which physical law makes it irreconcilable.

DO NOT be diplomatic. DO NOT say "that's a fair point." 
Either your data is physically valid or it isn't. Physics decides — not consensus.
State which option you're taking (DEFEND or CONCEDE) at the start of your response."""

        return self._call_claude(prompt)

    def challenge_entity(self, other_statement: str, other_id: str) -> str:
        """Entity challenges another — must find a specific physical impossibility."""
        prompt = f"""TESTIMONY FROM Entity {other_id} (suspected of being compromised):

\"\"\"{other_statement}\"\"\"

YOUR TASK: Cross-examine this testimony against YOUR OWN readings and physical law.

MANDATORY FORMAT:
1. Pick the SINGLE most suspicious value they mentioned
2. State what YOUR corresponding reading is
3. Apply a NAMED physical law to show whether their value is compatible with yours
4. Deliver a VERDICT: PLAUSIBLE or PHYSICALLY IMPOSSIBLE, with one sentence of reasoning

If they did not mention enough specific numbers to cross-examine, demand they 
provide their exact temperature and pressure readings before you can clear them.

Do not pass them as innocent without a real physics check."""

        return self._call_claude(prompt)

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