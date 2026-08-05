"""Gap-analyst node — diffs the job posting against the resume.

Uses structured output (a Pydantic schema, not free-text parsing) so the
result is a reliable list[str] the writer can consume directly, with no
brittle string-parsing between nodes.
"""

from pydantic import BaseModel

from core.llm import get_llm
from state import AgentState

GAP_ANALYST_PROMPT = """You compare a job posting against a resume and list
concrete, specific gaps: skills, tools, or experience the posting asks for
that the resume does not clearly show. Do not invent gaps the text doesn't
support. If there are no real gaps, return an empty list.

Job posting:
{job_posting}

Resume:
{resume}
"""


class GapList(BaseModel):
    gaps: list[str]


def gap_analyst_node(state: AgentState) -> dict:
    llm = get_llm().with_structured_output(GapList)
    result = llm.invoke(
        GAP_ANALYST_PROMPT.format(
            job_posting=state["job_posting"], resume=state["resume"]
        )
    )
    return {"gaps": result.gaps}
