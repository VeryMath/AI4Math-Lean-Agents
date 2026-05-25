# Gemini Instructions

For Lean 4 formal verification tasks, use the skill instructions at:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

The agent should directly inspect and edit Lean files, validate with Lean/Lake, preserve theorem statements, and avoid final patches with `sorry`, `admit`, or new `axiom`.

Match the user's language by default.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.

The helper CLI under `skills/AI4Math-Lean-Agents/scripts/` is optional tooling, not an external proof backend. It can report and configure the official Numina runtime when the user explicitly wants that path, but the agent should still validate final Lean patches locally.
