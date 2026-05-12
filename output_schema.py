from pydantic import BaseModel, Field
from typing import List, Dict, Any


class PhysicsMatrix(BaseModel):
    """
    Explains the cross-variable thermodynamic reasoning used to
    identify which nodes were lying and why.
    """
    invariants_used: List[str] = Field(
        description="The physical variables that were treated as ground truth anchors"
    )
    contradictions_found: List[str] = Field(
        description="Specific physical impossibilities identified during the dialectic"
    )
    reasoning_summary: str = Field(
        description="Plain-language explanation of the thermodynamic logic used"
    )


class ResolutionOutput(BaseModel):
    """
    The final output of the Cognitive Arbitration Engine.
    This is what gets printed/saved at the end of the run.
    """
    absolute_truth_state: Dict[str, Any] = Field(
        description="The synthesized true reactor state — best estimate of real values"
    )
    compromised_node_ids: List[str] = Field(
        description="Node IDs that were identified as producing false telemetry"
    )
    physics_matrix: PhysicsMatrix = Field(
        description="The reasoning chain that led to this conclusion"
    )
    confidence_level: str = Field(
        description="HIGH / MEDIUM / LOW — how certain the swarm is"
    )
    dialectic_rounds_completed: int = Field(
        description="How many rounds of debate occurred before consensus"
    )