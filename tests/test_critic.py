"""Unit tests for the critic node and its routing logic. Mocks get_llm
so grounding checks run without a live model call.
"""

from typing import cast
from unittest.mock import MagicMock, patch

from nodes.critic import MAX_ITERATIONS, CritiqueResult, critic_node, route_after_critic
from state import AgentState


def test_critic_node_returns_grounded_result():
    fake_llm = MagicMock()
    fake_llm.with_structured_output.return_value.invoke.return_value = CritiqueResult(
        grounded=True, issues=[]
    )
    with patch("nodes.critic.get_llm", return_value=fake_llm):
        result = critic_node(cast(AgentState, {"research_notes": [], "draft": "some draft"}))

    assert result["critique"] == {"grounded": True, "issues": []}


def test_route_after_critic_sends_to_human_review_when_grounded():
    state = cast(AgentState, {"critique": {"grounded": True, "issues": []}, "iteration_count": 1})
    assert route_after_critic(state) == "human_review"


def test_route_after_critic_loops_back_to_writer_when_ungrounded_and_under_cap():
    state = cast(AgentState, {
        "critique": {"grounded": False, "issues": ["no source"]},
        "iteration_count": 1,
    })
    assert route_after_critic(state) == "writer"


def test_route_after_critic_stops_looping_at_max_iterations():
    state = cast(AgentState, {
        "critique": {"grounded": False, "issues": ["still no source"]},
        "iteration_count": MAX_ITERATIONS,
    })
    assert route_after_critic(state) == "human_review"
