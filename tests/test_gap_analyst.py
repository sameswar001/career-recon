"""Unit test for the gap-analyst node. Mocks get_llm so this runs without
a live model call (no Ollama server, no API key) — deliberate, same
reasoning as test_researcher.py.
"""

from typing import cast
from unittest.mock import MagicMock, patch

from nodes.gap_analyst import GapList, gap_analyst_node
from state import AgentState


def test_gap_analyst_node_returns_llm_gaps():
    fake_llm = MagicMock()
    fake_llm.with_structured_output.return_value.invoke.return_value = GapList(
        gaps=["No mention of Kubernetes experience"]
    )
    with patch("nodes.gap_analyst.get_llm", return_value=fake_llm):
        result = gap_analyst_node(
            cast(AgentState, {"job_posting": "Requires Kubernetes", "resume": "No k8s mentioned"})
        )

    assert result["gaps"] == ["No mention of Kubernetes experience"]
