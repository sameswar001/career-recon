"""CLI entrypoint for career-recon.

Runs the graph against a real company, job posting, and resume, using a
SQLite-backed checkpointer so a paused run survives even if you quit
between the interrupt and your approval — resume it later with the
same --thread-id instead of re-running the research and writing from
scratch.
"""

import argparse
import uuid

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from graph.graph import build_graph

DB_PATH = "career_recon.db"


def _read(path_or_text: str) -> str:
    """Treats the argument as a file path if it exists, else raw text —
    so --job-posting works whether you pass a file or paste text inline.
    """
    try:
        with open(path_or_text) as f:
            return f.read()
    except FileNotFoundError:
        return path_or_text


def _prompt_for_decision(interrupt_payload: dict) -> dict:
    print("\n--- Draft for review ---\n")
    print(interrupt_payload.get("draft", ""))
    print("\n--- Gaps identified ---")
    for gap in interrupt_payload.get("gaps", []):
        print(f"- {gap}")

    while True:
        choice = input("\nApprove this brief? [y/n]: ").strip().lower()
        if choice == "y":
            return {"approved": True, "feedback": ""}
        if choice == "n":
            feedback = input("What should change? ").strip()
            return {"approved": False, "feedback": feedback}
        print("Please answer y or n.")


def run(company: str, job_posting: str, resume: str, thread_id: str) -> None:
    print(f"Starting run (thread_id: {thread_id})")
    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        checkpointer.setup()
        app = build_graph(checkpointer=checkpointer)
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        result = app.invoke(
            {"company": company, "job_posting": job_posting, "resume": resume, "iteration_count": 0},
            config,
        )

        while "__interrupt__" in result:
            payload = result["__interrupt__"][0].value
            decision = _prompt_for_decision(payload)
            result = app.invoke(Command(resume=decision), config)

        print("\n--- Final brief ---\n")
        print(result["draft"])
        print(f"\n(thread_id: {thread_id} — saved in {DB_PATH})")


def resume_thread(thread_id: str) -> None:
    with SqliteSaver.from_conn_string(DB_PATH) as checkpointer:
        checkpointer.setup()
        app = build_graph(checkpointer=checkpointer)
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

        state = app.get_state(config)
        pending = [i for task in state.tasks for i in task.interrupts]
        if not pending:
            print(f"No pending interrupt found for thread_id={thread_id}.")
            return

        decision = _prompt_for_decision(pending[0].value)
        result = app.invoke(Command(resume=decision), config)

        while "__interrupt__" in result:
            payload = result["__interrupt__"][0].value
            decision = _prompt_for_decision(payload)
            result = app.invoke(Command(resume=decision), config)

        print("\n--- Final brief ---\n")
        print(result["draft"])


def main() -> None:
    parser = argparse.ArgumentParser(description="career-recon: interview-prep agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="Start a new prep-brief run")
    start.add_argument("--company", required=True)
    start.add_argument("--job-posting", required=True, help="File path or raw text")
    start.add_argument("--resume", required=True, help="File path or raw text")
    start.add_argument("--thread-id", default=None)

    resume_cmd = subparsers.add_parser("resume", help="Resume a paused run")
    resume_cmd.add_argument("--thread-id", required=True)

    args = parser.parse_args()

    if args.command == "start":
        thread_id = args.thread_id or str(uuid.uuid4())
        run(args.company, _read(args.job_posting), _read(args.resume), thread_id)
    elif args.command == "resume":
        resume_thread(args.thread_id)


if __name__ == "__main__":
    main()
