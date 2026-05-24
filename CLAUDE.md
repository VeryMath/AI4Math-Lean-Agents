# Claude Code Instructions

For Lean work in this repository, read and follow:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

Use Claude Code as the direct Lean coding agent. Edit Lean files directly, run Lean/Lake checks frequently, and use the helper CLI only for deterministic checks such as environment inspection, optional Numina readiness/setup, patch review, `sorry` detection, and minimal failure extraction.

Match the user's language by default.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.

Deploy or call the official Numina runtime only when the user asks for it or approves it after an explanation. Keep secrets in environment variables or ignored local files.
