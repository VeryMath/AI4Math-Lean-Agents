# Lean Formalization

`lean-formalization` is the concrete AI4Math skill entrypoint for Lean 4
formalization, proof repair, theorem transcription, `sorry` completion, Lean
patch review, local validation, and optional Lean-specialist backend adapter
work currently implemented for official Numina.

## Entry Point

Start with [`SKILL.md`](SKILL.md). It defines the coding-agent-first workflow,
the optional backend boundary, safety rules, and the reference files to load
for specific tasks.

## Runtime Support

The reusable implementation lives in the sibling `../lean-runtime/` support
layer. It contains helper scripts, task-specific references, prompts, examples,
schemas, configuration templates, and tests. Keep `lean-runtime` installed next
to this entrypoint.

## Validation

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

## Related Work and Public References

This package is informed by public Lean ecosystem and Lean-agent projects:

- [Lean](https://lean-lang.org/) and [mathlib4](https://github.com/leanprover-community/mathlib4)
- [Numina Lean Agent](https://github.com/project-numina/numina-lean-agent)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo), [ReProver](https://github.com/lean-dojo/ReProver), and [LeanCopilot](https://github.com/lean-dojo/LeanCopilot)
- [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp)
- [COPRA](https://github.com/trishullab/copra)

They are cited as related work and design provenance, not bundled dependencies
or claims of compatibility.
