---
name: ai4math-lean-agents
description: Use when a coding agent needs Lean 4 formalization, proof repair, theorem transcription, sorry completion, Lean patch review, Numina runtime setup, or local Lean validation.
---

# AI4Math Lean Agents

This root `SKILL.md` is a compatibility entrypoint for platforms that expect one
top-level Skill file. The shared Skill layer lives at:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

Read that concrete Skill before Lean work. Keep platform adapters thin and
improve the shared Skill layer first.

## Operating Boundary

- Preserve theorem statements unless the user approves a change.
- Reject final patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Explain and approve optional Numina runtime setup before executing it.
- Validate final Lean patches locally when possible.
