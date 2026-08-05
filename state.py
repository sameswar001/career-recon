"""Shared graph state for career-recon.

This TypedDict is threaded through every node in the graph. Nodes return
partial dicts (LangGraph merges them into this state) rather than mutating
it directly.
"""

from typing import NotRequired, TypedDict


class ResearchNote(TypedDict):
    """A single piece of research, tied back to where it came from.

    Keeping source_url alongside content (rather than just prose) is what
    lets the critic later verify claims are actually grounded.
    """
    content: str
    source_url: str


class Critique(TypedDict):
    """Result of the critic's grounding check on a draft."""
    grounded: bool
    issues: list[str]


class AgentState(TypedDict):
    """State threaded through every node in the graph.

    Only company/job_posting/resume/iteration_count are supplied at
    invoke time; the rest are filled in by nodes as the graph runs, so
    they're NotRequired rather than missing-field errors under invoke()'s
    AgentState typing.
    """
    company: str
    job_posting: str
    resume: str
    iteration_count: int
    research_notes: NotRequired[list[ResearchNote]]
    gaps: NotRequired[list[str]]
    draft: NotRequired[str]
    critique: NotRequired[Critique]
    human_feedback: NotRequired[str]
    approved: NotRequired[bool]
