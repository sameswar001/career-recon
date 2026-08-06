"""Unit test for the researcher node. Mocks search_company so this runs
without a real TAVILY_API_KEY or network access — that's deliberate,
not a stand-in for real coverage. See test_graph_skeleton.py for the
live, credential-gated end-to-end run.
"""

from typing import cast
from unittest.mock import patch

from nodes.researcher import researcher_node
from state import AgentState


def test_researcher_node_maps_search_results_to_notes():
    fake_results = [
        {"content": "Acme raised a Series B", "source_url": "https://example.com/a"},
    ]
    with patch("nodes.researcher.search_company", return_value=fake_results):
        result = researcher_node(cast(AgentState, {"company": "Acme Corp"}))

    assert result["research_notes"] == fake_results
