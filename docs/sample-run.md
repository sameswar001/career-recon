# Sample run

This walks through a single run against a real posting, with the output
lightly trimmed. The point of interest is the **critic loop** — iteration 1's
draft slips in a claim the research notes don't support, the critic rejects it,
and iteration 2 fixes it. That reject-and-revise cycle is the reason this is a
graph and not a linear script.

> The transcript below is illustrative of the intended behavior. Regenerate it
> against your own posting with the command at the bottom, since exact model
> output varies by provider and by day.

```
$ python cli.py start --company "Acme Robotics" \
    --job-posting jd.txt --resume resume.txt

Starting run (thread_id: 7c1f...e9)
  [researcher]  5 notes gathered
  [gap_analyst] 3 gaps identified
  [writer]      draft v1 written (iteration 1)
  [critic]      NOT grounded — 1 issue:
                - "Acme's Series C valued the company at $2B" — no research
                  note supports the $2B figure; the funding note lists the
                  round but not a valuation.
  [writer]      draft v2 written (iteration 2)  <- revising on critic feedback
  [critic]      grounded — 0 issues
```

At that point the graph hits the human-review interrupt and pauses:

```
--- Draft for review ---

## Company Snapshot
Acme Robotics recently closed a Series C round (https://example.com/funding).
Its current product focus is warehouse automation (https://example.com/product).
...

## Gaps to Address
- The role asks for ROS2 experience; your resume shows ROS1. Speak to the
  transferable fundamentals and any migration work you've done.
...

--- Gaps identified ---
- No mention of ROS2 experience
- Posting emphasizes fleet-scale deployment; resume is single-robot
- No cloud-robotics (AWS RoboMaker / Greengrass) experience shown

Approve this brief? [y/n]:
```

If you exit here instead of answering, the run is checkpointed. Resume it later:

```
$ python cli.py resume --thread-id 7c1f...e9
```

## Reproduce

```bash
python cli.py start --company "<company>" \
    --job-posting <path-or-text> --resume <path-or-text>
```
