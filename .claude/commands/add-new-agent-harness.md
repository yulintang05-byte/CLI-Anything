---
name: add-new-agent-harness
description: Workflow command scaffold for add-new-agent-harness in CLI-Anything.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-agent-harness

Use this workflow when working on **add-new-agent-harness** in `CLI-Anything`.

## Goal

Adds a new tool integration (agent harness) to CLI-Anything, including CLI, core modules, utils, tests, and documentation.

## Common Files

- `<tool>/agent-harness/<TOOL>.md`
- `<tool>/agent-harness/cli_anything/<tool>/README.md`
- `<tool>/agent-harness/cli_anything/<tool>/__init__.py`
- `<tool>/agent-harness/cli_anything/<tool>/__main__.py`
- `<tool>/agent-harness/cli_anything/<tool>/<tool>_cli.py`
- `<tool>/agent-harness/cli_anything/<tool>/core/*.py`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create tool-specific directory under <tool>/agent-harness/
- Add <TOOL>.md and HARNESS.md (optional) for documentation
- Implement CLI entrypoint: cli_anything/<tool>/<tool>_cli.py (and sometimes __main__.py)
- Implement core modules: cli_anything/<tool>/core/*.py (project/session/export/etc.)
- Add utils: cli_anything/<tool>/utils/*.py (backend wrappers, REPL skins, etc.)

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.