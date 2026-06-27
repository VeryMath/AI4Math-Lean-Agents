# Agent Instructions

Use `skills/lean-setup/SKILL.md` for setup-only tasks such as installing or verifying Lean 4, `elan`, `lake`, or a reusable mathlib workspace.
Use the canonical shared Skill layer at `skills/lean-formalization/SKILL.md` for Lean 4 formalization, proof repair, theorem transcription, `sorry` completion, Lean patch review, optional Lean-specialist backend adapter work currently implemented for official Numina Lean Agent runtime deployment/calls, local Lean validation, and minimal failure handoff.
Reusable scripts, examples, prompts, schemas, and references live in the non-user-facing support layer at `skills/lean-runtime/`; install it alongside the two public Skill entrypoints.

Core rules:

- This is a coding-agent-first Lean skill.
- The coding agent is the primary Lean worker.
- Setup-only mode should not ask for a theorem target.
- Official Numina is the only currently supported deployable backend adapter; Archon and other backends are future adapters until an adapter contract, setup path, call path, and local validation gates are implemented.
- Match the user's language by default.
- If the user's language is ambiguous, default to Chinese.
- Lead the interaction: inspect context, summarize what is ready, recommend the next useful step, and ask at most one blocking question.
- Do not treat a language switch as a task reset; keep the current diagnosis and continue leading in the new language.
- When no target is provided, run or propose a safe local smoke/readiness check before asking for more input.
- Use the bundled smoke test when no user target is available.
- Formalization/proof readiness should inspect local Lean readiness first; inspect Numina/backend readiness only when the user asks for an optional Lean-specialist backend.
- Setup-only readiness should focus on local Lean/mathlib state, and should mention or inspect Numina only when the user asks for the optional official backend.
- Do not require API keys for the default coding-agent path.
- Shared workspace is the default Lean project context for standalone work; Numina may target it instead of upstream examples.
- Prefer the user's existing Lake project. Use the shared `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` only when a standalone file needs project context, and default that managed workspace to `leanprover/lean4:v4.28.0` unless the user explicitly overrides it.
- Use `${AI4MATH_HOME:-~/.ai4math}/lean-workspaces/<version-key>/` for standalone tasks that need a different Lean/mathlib revision; do not overwrite the canonical managed workspace for version drift.
- Preserve theorem statements unless the user explicitly approves a change.
- Reject final patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Do not commit API keys, local runtime state, or machine-specific Numina paths.

Useful validation:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```
