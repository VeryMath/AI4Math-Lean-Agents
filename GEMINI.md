# Gemini Instructions

For Lean 4 formal verification tasks, use the skill instructions at:

```text
skills/AI4Math-Lean-Agents/SKILL.md
```

In this skill, Lean Agent means the official Numina Lean Agent runtime. The coding agent orchestrates Numina deployment, configuration, invocation, and local Lean validation. Direct Lean editing is a validation and fallback path, not the default Lean Agent mode.

Match the user's language by default. If the user's language is ambiguous, default to Chinese.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
Opening readiness should inspect Numina readiness before recommending work.
Do not say API keys are unnecessary until the Numina mode is clear.
Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

The helper CLI under `skills/AI4Math-Lean-Agents/scripts/` is optional tooling. It can report and configure the official Numina runtime, but the agent should still validate final Lean patches locally.
