"""Human-review node — pauses for approval before finalizing the brief.

Stub for now: auto-approves so the skeleton graph can run end to end
without a real interrupt(). The real interrupt() + checkpointer lands
in a later step.
"""

from state import AgentState


def human_review_node(state: AgentState) -> dict:
    return {"approved": True, "human_feedback": ""}


def route_after_human_review(state: AgentState) -> str:
    if state.get("approved"):
        return "finalize"
    return "writer"
