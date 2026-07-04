# kaji-starter-python

Language: English | [Japanese](README.ja.md)

A Python starter repository that is ready to run [kaji](https://github.com/apokamo/kaji)'s
issue-driven development workflow (design → implement → review → PR) from the start.

- Python project skeleton (`src/` layout / `uv` / `ruff` / `mypy` / `pytest` / `Makefile`)
- kaji preinstalled (as a dev dependency; run it with `uv run kaji`)
- Five workflow YAMLs (3 for the GitHub provider + 2 for the local provider, claude single-agent setup)
- 23 generalized skills (`.claude/skills/`; non-Claude agents reference them via `.agents/skills/`)

Supported environments: Linux / macOS / WSL2 (native Windows is not supported — use WSL2).

## Quickstart

Prerequisites: [uv](https://docs.astral.sh/uv/) / [gh](https://cli.github.com/) / tmux 3.1+ /
an agent CLI (the default is [Claude Code](https://claude.com/claude-code); switch to
codex / gemini with `scripts/set_agent.py`).

```bash
# 1. On GitHub, click "Use this template" to create your own repository, then clone it

# 2. Initial setup commit (land it on main before running any workflow)
#    - .kaji/config.toml: set [provider.github] repo = "<owner>/<repo>" to your repo
#    - (optional) rename the pyproject.toml project name and src/starter_app/
git add -A && git commit -m "chore: initial setup"
#    ^ If left uncommitted, this setup change leaks into your first feature PR.

# 3. Set up and run the quality gate
uv sync
source .venv/bin/activate && make check   # passes right after creation

# 4. GitHub auth and label creation
gh auth status
scripts/setup_labels.sh                    # create the type:* labels the workflow uses (first time only)

# 5. Run the first workflow
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
uv run kaji run .kaji/wf/dev.yaml <issue-id>
```

GitHub labels (`type:*`) are not copied by "Use this template", so create them once with
`scripts/setup_labels.sh` (the workflow's issue creation depends on these labels).

To try it without GitHub, use the local provider (issues are created under the local
provider; no labels needed):

```bash
uv run kaji local init
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
uv run kaji run .kaji/wf/dev-local.yaml <issue-id>
```

## Documentation

- Setup details, development flow, and customization: the kaji usage guide (in preparation;
  track progress at [apokamo/kaji#242](https://github.com/apokamo/kaji/issues/242))
- Development conventions for this repository: [docs/README.md](docs/README.md)
- Agent instructions: [AGENTS.md](AGENTS.md)
