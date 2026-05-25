# Agent Instructions

Use the canonical skill at `skills/AI4Math-Lean-Agents/SKILL.md` for Lean 4 formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, optional official Numina runtime deployment/calls, and minimal failure handoff.

Core rules:

- The coding agent directly operates Lean; do not treat helper CLI commands as a proof backend.
- Numina is optional: deploy or call the official runtime only through the human-in-the-loop flow in `references/numina_runtime.md`.
- Match the user's language by default.
- Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
- Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
- When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
- Opening readiness should inspect both direct Lean and optional Numina status before recommending work.
- Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.
- Prefer the user's existing Lake project. Use the shared `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` only when a standalone file needs project context.
- Preserve theorem statements unless the user explicitly approves a change.
- Reject final patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Do not commit API keys, local runtime state, or machine-specific Numina paths.

Useful validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
