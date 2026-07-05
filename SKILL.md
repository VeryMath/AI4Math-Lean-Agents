---
name: lean-formalization
description: Use when a coding agent needs Lean 4 formalization, proof repair, theorem transcription, sorry completion, Lean patch review, optional adapter-first Lean-specialist backend work, or local Lean validation.
---

# Lean Formalization

This root `SKILL.md` is a compatibility entrypoint for platforms that expect one
top-level Skill file. The shared Skill layer lives at:

```text
skills/lean-formalization/SKILL.md
```

Read that concrete Skill before formalization or proof work. Keep platform
adapters thin and improve the shared Skill layer first.

Reusable scripts, prompts, examples, references, schemas, and tests live in:

```text
skills/lean-runtime/
```

For setup-only tasks such as installing Lean, checking `elan`/`lake`, or creating
a reusable mathlib workspace, use:

```text
skills/lean-setup/SKILL.md
```

## Operating Boundary

- Preserve theorem statements unless the user approves a change.
- Reject final patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Explain and approve optional backend runtime setup before executing it; use an adapter-first contract, with official Numina and Archon treated as recommended adapter candidates rather than hard requirements.
- Validate final Lean patches locally when possible.
