"""Live end-to-end run through the real researcher, gap-analyst, writer,
and critic nodes, plus a scripted approval through the human_review
interrupt (only the "a human actually clicks approve" part is
simulated — everything upstream of it is real). Skipped without a
TAVILY_API_KEY, since it makes a real search call and real LLM calls
rather than mocking them.
"""

import os

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from graph.graph import build_graph

pytestmark = pytest.mark.skipif(
    not os.environ.get("TAVILY_API_KEY"),
    reason="requires TAVILY_API_KEY and a reachable LLM provider for a live run",
)


def test_skeleton_runs_end_to_end():
    app = build_graph(checkpointer=MemorySaver())
    config: RunnableConfig = {"configurable": {"thread_id": "skeleton-test"}}

    paused = app.invoke(
        {
            "company": "Anthropic",
            "job_posting": "stub JD",
            "resume": "stub resume",
            "iteration_count": 0,
        },
        config,
    )
    assert "__interrupt__" in paused  # paused for human review

    result = app.invoke(Command(resume={"approved": True, "feedback": ""}), config)

    assert result["approved"] is True
    assert result["research_notes"]
    assert result["gaps"] is not None
    assert result["draft"]
