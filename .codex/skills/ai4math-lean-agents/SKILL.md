---
name: ai4math-lean-agents
description: Use for interactive Lean 4 formal verification with reusable Lean/mathlib workspaces, direct coding-agent proof repair, theorem formalization, sorry completion, patch review, and minimal failure handoff.
---

# AI4Math Lean Agents Repo Shim

This repo-local shim points to the canonical skill:

```text
../../../skills/AI4Math-Lean-Agents/SKILL.md
```

Read that file and follow it as the source of truth. The coding agent should directly operate Lean; helper CLI commands are guardrails, not a proof backend.
For evolved adaptive-ADMM `update_rho` candidates, route through the bundled `autoadmm-formalization` subskill before rendering Lean.
