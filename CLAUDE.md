# Claude Code Instructions

For Lean work in this repository, read and follow the shared Skill layer:

```text
skills/lean-formalization/SKILL.md
```

Use Claude Code as the Numina orchestrator and local Lean validator. In this skill, Lean Agent means the official Numina Lean Agent runtime. Direct Lean editing is a validation and fallback path, not the default Lean Agent mode.

Match the user's language by default. If the user's language is ambiguous, default to Chinese.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
Use the bundled smoke test when no user target is available.
Opening readiness should inspect Numina readiness before recommending work.
Do not say API keys are unnecessary until the Numina mode is clear.
Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

Deploy or call the official Numina runtime only after explanation and approval. Keep secrets in environment variables or ignored local files.
