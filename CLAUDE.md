# Claude Code Instructions

For Lean setup-only work in this repository, read and follow:

```text
skills/lean-setup/SKILL.md
```

For Lean formalization or proof work in this repository, read and follow the shared Skill layer:

```text
skills/lean-formalization/SKILL.md
```

Use Claude Code as the primary Lean coding agent. Official Numina is an optional deployable subagent backend; preserve that setup/call path but do not make it the default.
Setup-only mode should create or verify the Lean/mathlib workspace without asking for a theorem target.

Match the user's language by default. If the user's language is ambiguous, default to Chinese.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
Use the bundled smoke test when no user target is available.
Opening readiness should inspect local Lean readiness and Numina subagent readiness separately.
Do not require API keys for the default coding-agent path.
Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

Deploy or call the official Numina subagent runtime only after explanation and approval. Keep secrets in environment variables or ignored local files.
