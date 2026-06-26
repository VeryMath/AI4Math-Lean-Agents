# Claude Code Instructions

For Lean setup-only work in this repository, read and follow:

```text
skills/lean-setup/SKILL.md
```

For Lean formalization or proof work in this repository, read and follow the shared Skill layer:

```text
skills/lean-formalization/SKILL.md
```

Shared helper scripts, references, prompts, schemas, examples, and tests live in:

```text
skills/lean-runtime/
```

Use Claude Code as the primary Lean coding agent. Official Numina is the only currently supported deployable backend adapter; preserve that setup/call path but do not make it the default. Archon and other backends are future adapters until their setup, call, credential, mutation, and validation contracts are documented.
Setup-only mode should create or verify the Lean/mathlib workspace without asking for a theorem target.

Match the user's language by default. If the user's language is ambiguous, default to Chinese.
Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
Use the bundled smoke test when no user target is available.
Formalization/proof readiness should inspect local Lean readiness first; inspect Numina/backend readiness only when the user asks for an optional Lean-specialist backend.
Setup-only readiness should focus on local Lean/mathlib state, and should mention or inspect Numina only when the user asks for the optional official backend.
Do not require API keys for the default coding-agent path.
Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

Deploy or call the official Numina backend runtime only after explanation and approval. Keep secrets in environment variables or ignored local files.
