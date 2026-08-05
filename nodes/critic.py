"""Critic node — checks the draft's claims against research_notes.

Stub for now: always reports grounded=True so the skeleton graph can
prove its shape end to end. Real claim-by-claim grounding checks land
in a later step.
"""

from state import AgentState

MAX_ITERATIONS = 3


def critic_node(state: AgentState) -> dict:
    return {"critique": {"grounded": True, "issues": []}}


def route_after_critic(state: AgentState) -> str:
    """Loop back to the writer on ungrounded claims, capped at MAX_ITERATIONS."""
    critique = state.get("critique", {"grounded": True, "issues": []})
    if not critique.get("grounded", True) and state.get("iteration_count", 0) < MAX_ITERATIONS:
        return "writer"
    return "human_review"
