"""Unit tests for the writer node. Mocks get_llm so this runs without a
live model call — same reasoning as test_researcher.py / test_gap_analyst.py.
"""

from typing import cast
from unittest.mock import MagicMock, patch

from nodes.writer import writer_node
from state import AgentState


def test_writer_node_drafts_from_notes_and_gaps():
    fake_llm = MagicMock()
    fake_llm.invoke.return_value.content = "## Company Snapshot\n..."

    state = cast(AgentState, {
        "company": "Acme Corp",
        "research_notes": [
            {"content": "Acme raised a Series B", "source_url": "https://example.com/a"}
        ],
        "gaps": ["No mention of Kubernetes experience"],
        "iteration_count": 0,
    })

    with patch("nodes.writer.get_llm", return_value=fake_llm):
        result = writer_node(state)

    assert result["draft"].startswith("## Company Snapshot")
    assert result["iteration_count"] == 1


def test_writer_node_includes_revision_feedback_on_ungrounded_critique():
    fake_llm = MagicMock()
    fake_llm.invoke.return_value.content = "revised draft"

    with patch("nodes.writer.get_llm", return_value=fake_llm):
        writer_node(
            cast(AgentState, {
                "company": "Acme Corp",
                "research_notes": [],
                "gaps": [],
                "iteration_count": 1,
                "draft": "previous draft text",
                "critique": {"grounded": False, "issues": ["claim X has no source"]},
            })
        )

    prompt_sent = fake_llm.invoke.call_args[0][0]
    assert "claim X has no source" in prompt_sent
    assert "previous draft text" in prompt_sent
