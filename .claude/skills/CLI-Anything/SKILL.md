```markdown
# CLI-Anything Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you how to contribute to the CLI-Anything project, a Python-based codebase for building agent-native CLI harnesses and skill/plugin integrations for various external tools and platforms. You'll learn the project's coding conventions, common workflows (like adding new agent harnesses or skills), and how to structure and document your contributions for consistency and maintainability.

---

## Coding Conventions

**File Naming**
- Use `snake_case` for Python files and directories.
  - Example: `my_tool_cli.py`, `test_core.py`

**Import Style**
- Use relative imports within packages.
  - Example:
    ```python
    from .core import session_manager
    from .utils.repl_skin import apply_skin
    ```

**Export Style**
- Default exports (no explicit `__all__` unless needed).

**Commit Patterns**
- Mixed types, with prefixes like `fix`, `docs`, `feat`.
- Commit messages are concise (average ~48 characters).
  - Example: `fix: handle edge case in session export`

---

## Workflows

### Add New Agent Harness
**Trigger:** When adding support for a new external tool or platform as an agent-native CLI harness.  
**Command:** `/new-harness`

1. Create a tool-specific directory: `<tool>/agent-harness/`
2. Add documentation files: `<TOOL>.md` and optionally `HARNESS.md`
3. Implement CLI entrypoint:
    - `cli_anything/<tool>/<tool>_cli.py`
    - Optionally `__main__.py`
4. Implement core modules:
    - `cli_anything/<tool>/core/*.py` (e.g., `project.py`, `session.py`, `export.py`)
5. Add utility modules:
    - `cli_anything/<tool>/utils/*.py` (e.g., `backend_wrapper.py`, `repl_skin.py`)
6. Add tests:
    - `cli_anything/<tool>/tests/__init__.py`
    - `cli_anything/<tool>/tests/test_core.py`
    - `cli_anything/<tool>/tests/test_full_e2e.py`
    - `cli_anything/<tool>/tests/TEST.md`
7. Add or update `setup.py` in `agent-harness/`
8. Update `.gitignore` and `README.md` as needed

**Example Directory Structure:**
```
audacity/
  agent-harness/
    AUDACITY.md
    HARNESS.md
    cli_anything/
      audacity/
        __init__.py
        __main__.py
        audacity_cli.py
        core/
          project.py
          session.py
        utils/
          backend_wrapper.py
        tests/
          __init__.py
          test_core.py
          test_full_e2e.py
          TEST.md
    setup.py
```

---

### Add New Skill or Plugin Command
**Trigger:** When adding a new skill (e.g., Codex) or plugin command to CLI-Anything.  
**Command:** `/new-skill`

1. Create a new skill/plugin directory (e.g., `codex-skill/` or `cli-anything-plugin/commands/`)
2. Add `SKILL.md` or command documentation
3. Add agent config YAML or command implementation script
4. Add or update install scripts if needed (e.g., `scripts/install.sh`)
5. Update `.gitignore`, `README.md`, and `README_CN.md`

**Example:**
```
codex-skill/
  SKILL.md
  agents/
    codex_agent.yaml
  scripts/
    install.sh
cli-anything-plugin/
  commands/
    my_command.md
  README.md
```

---

### Fix or Update setup.py Metadata
**Trigger:** When correcting or standardizing packaging metadata or dependencies across agent harnesses.  
**Command:** `/fix-setup-metadata`

1. Identify all `agent-harness/<tool>/setup.py` files
2. Update URLs, author, or dependency fields as needed
3. Commit all modified `setup.py` files together

**Example:**
```python
# In audacity/agent-harness/setup.py
setup(
    name="cli-anything-audacity",
    version="0.1.0",
    author="CLI-Anything Contributors",
    url="https://github.com/cli-anything/audacity",
    install_requires=[
        "some-dependency>=1.0.0"
    ],
    # ...
)
```

---

### Add or Update README and Docs
**Trigger:** When documenting a new feature, updating limitations, or clarifying usage in the main and localized READMEs.  
**Command:** `/update-docs`

1. Edit `README.md` and `README_CN.md`
2. Optionally update related documentation files (e.g., `cli-anything-plugin/README.md`)
3. Commit with a `docs-` or `update-` prefix

---

## Testing Patterns

- **Framework:** Unknown (no standard Python test framework detected; some test files use `.test.ts` pattern, possibly for TypeScript or as a naming convention).
- **File Pattern:** Test files are named as `test_*.py` (Python) or `*.test.ts` (TypeScript).
- **Test Structure:** Place test files in a `tests/` subdirectory within each tool/skill/plugin.
- **Documentation:** Each test suite may include a `TEST.md` describing test coverage and scenarios.

**Example:**
```
cli_anything/audacity/tests/
  __init__.py
  test_core.py
  test_full_e2e.py
  TEST.md
```

---

## Commands

| Command              | Purpose                                                         |
|----------------------|-----------------------------------------------------------------|
| /new-harness         | Scaffold and add a new agent harness for an external tool       |
| /new-skill           | Add a new skill integration or plugin command                   |
| /fix-setup-metadata  | Standardize or correct setup.py metadata across harnesses       |
| /update-docs         | Update README files and documentation                           |
```
