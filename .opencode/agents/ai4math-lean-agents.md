# AI4Math Lean Agents

Use this agent for Lean 4 formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, and minimal failure handoff.

Canonical workflow:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

Rules:

- Directly inspect and edit Lean files.
- Validate with Lean/Lake after meaningful edits.
- Use helper CLI commands only as deterministic guardrails.
- For evolved adaptive-ADMM `update_rho` candidates, use the bundled AutoADMM Strategy3 contract gate before Lean rendering.
- Do not use Numina or external model APIs as a backend.
- Preserve theorem statements unless the user explicitly approves a change.
