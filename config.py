import os
from dotenv import load_dotenv

# Load the .env file automatically
load_dotenv()

# --- API Settings ---
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1500"))

# --- Mock Mode (set by main.py) ---
MOCK_MODE: bool = False  # Will be set to True if --mock flag is used

# --- Debate Settings ---
MAX_DIALECTIC_ROUNDS: int = int(os.getenv("MAX_DIALECTIC_ROUNDS", "3"))

# --- Variable Decryption Map (from Appendix A of the brief) ---
# Maps the encrypted key names in the data to their real physical meaning
KEY_MAP: dict = {
    "v_m1": "Internal Thermal Kinetic Energy (°C)",
    "v_m2": "Containment Structural Stress / Pressure (psi)",
    "v_m3": "Ambient Electromagnetic Flux (Webers)",
    "v_m4": "Sub-surface Acoustic Resonance (Hz)",
    "v_m5": "Micro-seismic Vibrational Tremors (g-force)",
    "v_m6": "Fluid Kinematic Viscosity Index",
    "v_m7": "Background Gamma Attenuation Baseline (mSv/h)",
    "sys_log": "Automated Diagnostic Status String",
}

# --- Sanity Check ---
if not ANTHROPIC_API_KEY:
    raise EnvironmentError(
        "ANTHROPIC_API_KEY is not set. "
        "Copy .env.template to .env and add your key."
    )