# Agent Instructions

Use the canonical skill at `skills/AI4Math-Lean-Agents/SKILL.md` for Lean 4 formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, and minimal failure handoff.

Core rules:

- The coding agent directly operates Lean; do not treat helper CLI commands as a proof backend.
- Do not deploy or call Numina, Claude Code CLI, or external model APIs for this skill.
- Prefer the user's existing Lake project. Use `.ai4math/lean-workspace` only when a standalone file needs project context.
- Preserve theorem statements unless the user explicitly approves a change.
- Reject final patches containing `sorry`, `admit`, or newly introduced `axiom`.

Useful validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
