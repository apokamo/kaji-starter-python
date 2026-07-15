---
name: series-create
description: Create a validated sequential Issue series plan from an explicitly ordered GitHub Issue list. Use when a maintainer wants to generate or update an ID-named YAML file under .kaji/series, select standard workflows from Issue type metadata and workflow descriptions, or preview a series without starting it.
---

# Series Create

Generate a deterministic series YAML, validate it, show its dry-run plan, and stop before execution.

## Input

```text
/series-create <issue>... --id <series-id> [--parent <issue>]
  [--workflow <issue>=<repo-relative-path>]... [--update]
```

Preserve Issue order exactly. Require `--id` and at least one positive integer Issue number. Treat `--workflow` as a member-specific override.

## Workflow

1. Confirm `uv run kaji config provider-type` returns `github`; otherwise stop.
2. Read each Issue without mutation:

   ```bash
   uv run kaji issue view <issue> --json labels,title,state
   ```

3. Read every `.kaji/wf/*.yaml` `description` and `requires_provider` value. For each member without an override, select candidates whose description says they are the standard series auto-selection target for the Issue's single `type:` label and whose provider is `github` or `any`.
4. Auto-select only when exactly one candidate remains. Display the Issue type and matching description sentence as the reason. If selection is ambiguous, request `--workflow <issue>=<path>`.
5. Invoke the package-provided deterministic generator. Do not write YAML manually:

   ```bash
   uv run python -m kaji_harness.scripts.series_generate \
     --id <series-id> [--parent <parent>] \
     --member <issue>=<workflow>... \
     --output .kaji/series/<series-id>.yaml [--update]
   ```

6. If the target exists without `--update`, stop. Never retry with `--update` implicitly.
7. Run both checks and stop if either fails:

   ```bash
   uv run kaji validate-series .kaji/series/<series-id>.yaml
   uv run kaji run-series .kaji/series/<series-id>.yaml --dry-run
   ```

8. Report the path, ordered members, workflow selection reasons, validation result, and dry-run plan. Do not start `run-series` without `--dry-run`.

## Output

- One `.kaji/series/<id>.yaml` containing only the validated schema fields.
- A console summary of selection reasons and the dry-run plan.
- No Issue, PR, label, sub-issue, state, lock, or member-run mutation.

## Stop Conditions

- Provider is not GitHub.
- Input or Issue type metadata is missing or ambiguous.
- Workflow selection is not unique and no override was supplied.
- The output exists without explicit `--update`.
- Generation, validation, or dry-run returns nonzero.

## Non-goals

- Discovering members from an EPIC or sub-issue relation.
- Reordering members or inferring dependencies.
- Editing Issue metadata or external state.
- Starting actual series execution.
