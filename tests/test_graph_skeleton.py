"""Proves the graph's shape works before any real node logic exists:
fan-out from START, fan-in at writer, and a run that reaches the end
without error.
"""

import os

import pytest

from graph.graph import build_graph

pytestmark = pytest.mark.skipif(not os.environ.get("TAVILY_API_KEY"), reason="TAVILY_API_KEY not set; skipping graph skeleton test")
def test_skeleton_runs_end_to_end():
    app = build_graph()
    result = app.invoke(
        {
            "company": "Acme Corp",
            "job_posting": "stub JD",
            "resume": "stub resume",
            "iteration_count": 0,
        }
    )

    assert result["approved"] is True
    assert result["iteration_count"] == 1
    assert "stub draft" in result["draft"]
    assert result["research_notes"]
    assert result["gaps"]
