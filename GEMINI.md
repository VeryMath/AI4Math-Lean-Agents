# Gemini Instructions

For Lean 4 formal verification tasks, use the skill instructions at:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

The agent should directly inspect and edit Lean files, validate with Lean/Lake, preserve theorem statements, and avoid final patches with `sorry`, `admit`, or new `axiom`.

The helper CLI under `skills/AI4Math-Lean-Agents/scripts/` is optional tooling, not an external proof backend. It can report and configure the official Numina runtime when the user explicitly wants that path, but the agent should still validate final Lean patches locally.
