---
name: lean-setup
description: Use when a coding agent needs to install or verify Lean 4, elan, lake, create or reuse a mathlib workspace, configure a shared Lean environment, or run Lean readiness checks before formalization.
---

# Lean Setup

Use this setup-only entrypoint when the user only wants a Lean 4 environment, `elan`/`lake` readiness, or a reusable mathlib workspace. Do not ask for a theorem target in setup-only mode.

The canonical implementation lives in `../lean-formalization/`. This skill must reuse the same helper CLI, configuration rules, and runtime references rather than duplicating setup logic.

## Setup-Only Flow

1. Match the user's language by default; if ambiguous, default to Chinese.
2. Inspect tool and workspace readiness with `doctor` or `env`.
3. Prefer an existing Lake project when the user points to one.
4. For standalone future Lean work, create or reuse `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`.
5. Create the workspace only after explaining that Lean/mathlib artifacts may be downloaded or built.
6. Run the bundled smoke test after setup.
7. Report the installed tools, workspace path, Lean toolchain, mathlib revision when available, smoke-test result, and any remaining action.
8. If the user next wants formalization, proof repair, theorem transcription, `sorry` completion, patch review, or Numina proof search, hand off to `lean-formalization`.

## Commands

Run from the repository root:

```bash
python skills/lean-formalization/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-formalization/scripts/ai4m_lean.py env --cwd .
python skills/lean-formalization/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/lean-formalization/scripts/ai4m_lean.py smoke-test --cwd .
```

Use `--dry-run` before setup when the user wants to review commands.

## Boundaries

- Do not create a second setup implementation.
- Do not change a user project's `lean-toolchain` or mathlib revision without approval.
- Do not require API keys for Lean/mathlib workspace setup.
- Do not configure or call official Numina unless the user explicitly asks for that optional backend.
- Do not commit machine-specific paths, downloaded runtime state, or secrets.

## References

- Read `../lean-formalization/references/lean_runtime_configuration.md` for shared workspace layout, local configuration, and version policy.
- Read `../lean-formalization/references/numina_runtime.md` only when the user asks for optional official Numina setup.
- Use `../lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests` for package validation.
