"""Writer node — drafts the prep brief from research_notes and gaps.

Stub for now: returns a placeholder draft and bumps iteration_count, so
the critic/human-review loop has something real to increment against.
Real drafting logic lands in a later step.
"""

from state import AgentState


def writer_node(state: AgentState) -> dict:
    iteration = state.get("iteration_count", 0) + 1
    return {
        "draft": f"stub draft (iteration {iteration})",
        "iteration_count": iteration,
    }
