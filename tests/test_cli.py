"""Tests for the CLI's own logic — file-vs-text argument handling and
the interrupt/resume loop — isolated from the real graph via a fake
app object, same reasoning as the node-level tests: no network or LLM
calls needed to prove this control flow is correct.
"""

import builtins

from entrypoint import cli


class _FakeInterrupt:
    def __init__(self, value):
        self.value = value


class _FakeApp:
    """Stands in for the compiled graph so the CLI's resume loop can be
    tested without a real researcher/writer/critic chain behind it.
    """

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = 0

    def invoke(self, _input, _config):
        response = self._responses[self.calls]
        self.calls += 1
        return response


def test_read_returns_file_contents_when_path_exists(tmp_path):
    f = tmp_path / "jd.txt"
    f.write_text("a job posting")
    assert cli._read(str(f)) == "a job posting"


def test_read_returns_raw_text_when_not_a_path():
    assert cli._read("just some raw text, not a path") == "just some raw text, not a path"


def test_run_loops_through_interrupt_until_approved(tmp_path, monkeypatch):
    fake_app = _FakeApp(
        [
            {"__interrupt__": (_FakeInterrupt({"draft": "draft v1", "gaps": []}),)},
            {"approved": True, "draft": "draft v1"},
        ]
    )
    monkeypatch.setattr(cli, "build_graph", lambda checkpointer=None: fake_app)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": "y")
    monkeypatch.setattr(cli, "DB_PATH", str(tmp_path / "test.db"))

    cli.run("Acme Corp", "stub JD", "stub resume", "test-thread")

    assert fake_app.calls == 2


def test_run_asks_for_feedback_on_rejection(tmp_path, monkeypatch):
    fake_app = _FakeApp(
        [
            {"__interrupt__": (_FakeInterrupt({"draft": "draft v1", "gaps": []}),)},
            {"approved": True, "draft": "draft v2"},
        ]
    )
    monkeypatch.setattr(cli, "build_graph", lambda checkpointer=None: fake_app)
    responses = iter(["n", "make it shorter", "y"])
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(responses))
    monkeypatch.setattr(cli, "DB_PATH", str(tmp_path / "test.db"))

    cli.run("Acme Corp", "stub JD", "stub resume", "test-thread-2")

    assert fake_app.calls == 2
