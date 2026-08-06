"""Unit tests for the human-review node's interrupt/resume mechanics.

Builds a minimal graph containing only the human_review node, rather
than the full pipeline — interrupt() only behaves correctly inside a
real running, checkpointed graph, and isolating it here means these
tests don't need to mock the researcher/writer/critic chain just to
reach it. Uses MemorySaver (in-process, no disk I/O) since these tests
only need to prove the pause/resume mechanic within a single process;
SqliteSaver is for real cross-process persistence, wired up in the CLI.
"""

from typing import cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from nodes.human_review import human_review_node, route_after_human_review
from state import AgentState


def _build_test_graph():
    graph = StateGraph(AgentState)
    graph.add_node("human_review", human_review_node)
    graph.add_edge(START, "human_review")
    graph.add_conditional_edges(
        "human_review", route_after_human_review, {"finalize": END, "writer": END}
    )
    return graph.compile(checkpointer=MemorySaver())


def test_human_review_interrupts_then_resumes_on_approval():
    app = _build_test_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "test-approve"}}

    paused = app.invoke(cast(AgentState, {"draft": "some draft", "gaps": []}), config)
    assert "__interrupt__" in paused

    result = app.invoke(Command(resume={"approved": True, "feedback": ""}), config)
    assert result["approved"] is True


def test_human_review_carries_feedback_through_on_rejection():
    app = _build_test_graph()
    config: RunnableConfig = {"configurable": {"thread_id": "test-reject"}}

    app.invoke(cast(AgentState, {"draft": "some draft", "gaps": []}), config)
    result = app.invoke(
        Command(resume={"approved": False, "feedback": "add more detail"}), config
    )

    assert result["approved"] is False
    assert result["human_feedback"] == "add more detail"
