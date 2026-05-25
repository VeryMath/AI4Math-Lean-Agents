# Agent Instructions

Use the canonical skill at `skills/AI4Math-Lean-Agents/SKILL.md` for Lean 4 formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, official Numina Lean Agent runtime deployment/calls, local Lean validation, and minimal failure handoff.

Core rules:

- In this skill, Lean Agent means the official Numina Lean Agent runtime.
- The coding agent orchestrates Numina deployment, configuration, invocation, and local Lean validation.
- Direct Lean editing is a validation and fallback path, not the default Lean Agent mode.
- Match the user's language by default.
- If the user's language is ambiguous, default to Chinese.
- Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
- Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
- When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
- Opening readiness should inspect Numina readiness before recommending work.
- Do not say API keys are unnecessary until the Numina mode is clear.
- Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.
- Prefer the user's existing Lake project. Use the shared `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` only when a standalone file needs project context.
- Preserve theorem statements unless the user explicitly approves a change.
- Reject final patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Do not commit API keys, local runtime state, or machine-specific Numina paths.

Useful validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
