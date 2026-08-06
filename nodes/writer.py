"""Writer node — drafts the prep brief from research_notes and gaps.

Only asked to state facts that appear in research_notes, with a citation
after every claim, so the critic node (next step) has something concrete
to check grounding against. On a revision pass, the previous draft and
the critique or human feedback are folded back in so it's an edit, not a
fresh guess.
"""

from collections.abc import Sequence

from core.llm import get_llm
from state import AgentState, ResearchNote

WRITER_PROMPT = """You are drafting a concise interview-prep brief for {company}.

Only state facts that appear in the research notes below. After every
factual claim, cite its source in parentheses, e.g. (https://example.com).
Do not invent or assume anything the notes don't support.

Research notes:
{research_notes}

Resume gaps to address — for each, write a short note on how the candidate
could speak to it in an interview:
{gaps}
{revision_section}
Write the brief in markdown with two sections: "## Company Snapshot" and
"## Gaps to Address". Keep it under 400 words.
"""

REVISION_TEMPLATE = """
The previous draft had issues. Fix these specifically, using only the
research notes above:
{issues}

Previous draft:
{previous_draft}
"""


def _format_notes(notes: Sequence[ResearchNote]) -> str:
    if not notes:
        return "(none)"
    return "\n".join(f"- {n['content']} ({n['source_url']})" for n in notes)


def _format_gaps(gaps: list[str]) -> str:
    if not gaps:
        return "(none identified)"
    return "\n".join(f"- {g}" for g in gaps)


def writer_node(state: AgentState) -> dict:
    critique = state.get("critique")
    revision_section = ""
    if critique and not critique.get("grounded", True):
        revision_section = REVISION_TEMPLATE.format(
            issues="\n".join(f"- {i}" for i in critique.get("issues", [])),
            previous_draft=state.get("draft", ""),
        )
    elif human_feedback := state.get("human_feedback"):
        revision_section = REVISION_TEMPLATE.format(
            issues=human_feedback,
            previous_draft=state.get("draft", ""),
        )

    prompt = WRITER_PROMPT.format(
        company=state["company"],
        research_notes=_format_notes(state.get("research_notes", [])),
        gaps=_format_gaps(state.get("gaps", [])),
        revision_section=revision_section,
    )

    llm = get_llm()
    response = llm.invoke(prompt)
    iteration = state.get("iteration_count", 0) + 1

    return {"draft": response.content, "iteration_count": iteration}
