"""Human-review node — pauses for approval before finalizing the brief.

Uses LangGraph's interrupt() to actually suspend graph execution (not a
polling loop or a flag check) until a human resumes it with a real
decision. This only works because the graph is compiled with a
checkpointer — interrupt() persists state through it so execution can
pick back up exactly where it left off, potentially in a different
process entirely.
"""

from langgraph.types import interrupt

from state import AgentState


def human_review_node(state: AgentState) -> dict:
    decision = interrupt(
        {
            "draft": state.get("draft", ""),
            "gaps": state.get("gaps", []),
            "prompt": "Approve this brief, or provide feedback to revise it.",
        }
    )
    return {
        "approved": decision.get("approved", False),
        "human_feedback": decision.get("feedback", ""),
    }


def route_after_human_review(state: AgentState) -> str:
    if state.get("approved"):
        return "finalize"
    return "writer"
