"""Researcher node — gathers source-tracked notes about the target company.

No LLM call here on purpose: this node's job is to collect grounded raw
material with URLs attached. Synthesis into prose happens in the writer
node, and the critic checks that synthesis back against these notes —
that separation is what makes the grounding check possible at all.
"""

from state import AgentState
from tools.web_search import search_company


def researcher_node(state: AgentState) -> dict:
    results = search_company(state["company"])
    return {
        "research_notes": [
            {"content": r["content"], "source_url": r["source_url"]}
            for r in results
        ]
    }
