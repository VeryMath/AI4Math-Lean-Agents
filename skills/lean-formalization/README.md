# Lean Formalization

`lean-formalization` is the concrete AI4Math skill package for Lean 4
formalization, proof repair, theorem transcription, `sorry` completion, Lean
patch review, local validation, and optional official Numina runtime work.

## Entry Point

Start with [`SKILL.md`](SKILL.md). It defines the coding-agent-first workflow,
the optional Numina boundary, safety rules, and the reference files to load for
specific tasks.

## Package Layout

- `scripts/`: helper CLI commands for environment checks, validation, patch
  review, Numina setup, and delivery verification.
- `references/`: task-specific guidance for direct Lean workflows, runtime
  configuration, Numina, review, and failure reporting.
- `prompts/`: reusable task envelopes for formalization, proof repair, and
  `sorry` completion.
- `config/` and `schemas/`: example configuration and validation schemas.
- `tests/`: package-level Python tests for the helper CLI and validation logic.

## Validation

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
