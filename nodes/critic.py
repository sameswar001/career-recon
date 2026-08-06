"""Critic node — checks the draft's claims against research_notes.

Runs the same grounding-check discipline as the evaluation suite in
llm-eval-legal-rag, just applied to an agent's own draft instead of a
RAG pipeline's answer: does every claim trace back to a source, not
does the writing merely sound plausible.
"""

from collections.abc import Sequence
from typing import cast

from pydantic import BaseModel

from core.llm import get_llm
from state import AgentState, ResearchNote


MAX_ITERATIONS = 3

CRITIC_PROMPT = """Check this draft interview-prep brief for grounding.
Every factual claim must be supported by the research notes below, and
every cited URL must actually appear in the research notes.

Flag a claim if it:
- Is not supported by any research note, or
- Cites a URL that isn't in the research notes, or
- Has no citation at all despite being a specific factual claim

If everything is properly grounded and cited, return grounded=true with
an empty issues list. Otherwise return grounded=false and list each
issue specifically enough that it can be fixed.

Research notes:
{research_notes}

Draft:
{draft}
"""


class CritiqueResult(BaseModel):
    grounded: bool
    issues: list[str]


def _format_notes(notes: Sequence[ResearchNote]) -> str:
    if not notes:
        return "(none)"
    return "\n".join(f"- {n['content']} ({n['source_url']})" for n in notes)


def critic_node(state: AgentState) -> dict:
    llm = get_llm().with_structured_output(CritiqueResult)
    result = cast(
        CritiqueResult,
        llm.invoke(
            CRITIC_PROMPT.format(
                research_notes=_format_notes(state.get("research_notes", [])),
                draft=state.get("draft", ""),
            )
        ),
    )
    return {"critique": {"grounded": result.grounded, "issues": result.issues}}


def route_after_critic(state: AgentState) -> str:
    """Loop back to the writer on ungrounded claims, capped at MAX_ITERATIONS."""
    critique = state.get("critique", {"grounded": True, "issues": []})
    if not critique.get("grounded", True) and state.get("iteration_count", 0) < MAX_ITERATIONS:
        return "writer"
    return "human_review"
