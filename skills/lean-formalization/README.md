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

## References

This package learns from public Lean ecosystem and Lean-agent projects:

- [Lean](https://lean-lang.org/) and [mathlib4](https://github.com/leanprover-community/mathlib4)
- [Numina Lean Agent](https://github.com/project-numina/numina-lean-agent)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo), [ReProver](https://github.com/lean-dojo/ReProver), and [LeanCopilot](https://github.com/lean-dojo/LeanCopilot)
- [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp)
- [COPRA](https://github.com/trishullab/copra)

They are public design references, not bundled dependencies or claims of
compatibility.
