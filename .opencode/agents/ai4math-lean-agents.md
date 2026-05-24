# AI4Math Lean Agents

Use this agent for Lean 4 formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, optional official Numina runtime deployment/calls, and minimal failure handoff.

Canonical workflow:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

Rules:

- Directly inspect and edit Lean files.
- Match the user's language by default.
- Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
- Validate with Lean/Lake after meaningful edits.
- Use helper CLI commands only as deterministic guardrails.
- Use official Numina only through the approved human-in-the-loop runtime flow.
- Preserve theorem statements unless the user explicitly approves a change.
