# career-recon

Multi-agent system built with LangGraph. Given a target company and a job
posting, it researches the company, diffs the posting against a resume for
real gaps, and drafts an interview-prep brief — with a grounding critic that
rejects unsupported claims and loops the draft back for revision, and a
human-approval checkpoint before anything is finalized.

## Architecture

​```
Input (company + JD + resume)
        |
        v
Researcher & analyst (parallel: web search + resume diff)
        |
        v
Writer (drafts the prep brief)
        |
        v
Critic (checks grounding) -----> ↻ revises via writer
        |
        v
Human review (approve or changes) -----> ↻ requests changes (back to writer)
        |
        v
Output (final prep brief)
​```

State (`state.py`) is a shared `TypedDict` carrying `company`, `job_posting`,
`resume`, `research_notes` (source-tracked), `gaps`, `draft`, `critique`, and
`iteration_count` through every node.

## Status

Project scaffold only — pipeline stages below are being built incrementally,
one commit per stage.

- [x] Repo & environment scaffold
- [ ] State schema & graph skeleton
- [ ] Researcher & gap-analyst nodes
- [ ] Writer node
- [ ] Critic & revision loop
- [ ] Human-in-the-loop review
- [ ] Persistence & CLI entrypoint
- [ ] Polish & docs

## Setup

​```bash
uv sync
​```
