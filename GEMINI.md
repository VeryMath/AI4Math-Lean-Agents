# Gemini Instructions

For Lean 4 formal verification tasks, use the shared Skill layer at:

```text
skills/lean-formalization/SKILL.md
```

Use Gemini as the primary Lean coding agent. Official Numina is an optional deployable subagent backend; preserve that setup/call path but do not make it the default.

Match the user's language by default. If the user's language is ambiguous, default to Chinese.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
Use the bundled smoke test when no user target is available.
Opening readiness should inspect local Lean readiness and Numina subagent readiness separately.
Do not require API keys for the default coding-agent path.
Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

The helper CLI under `skills/lean-formalization/scripts/` is optional tooling. It can report and configure the official Numina subagent runtime, but the agent should still validate final Lean patches locally.
