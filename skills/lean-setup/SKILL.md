---
name: lean-setup
description: Use when a coding agent needs to install or verify Lean 4, elan, lake, create or reuse a mathlib workspace, configure a shared Lean environment, or run Lean readiness checks before formalization.
---

# Lean Setup

Use this setup-only entrypoint when the user only wants a Lean 4 environment, `elan`/`lake` readiness, or a reusable mathlib workspace. Do not ask for a theorem target in setup-only mode.

The shared implementation lives in `../lean-runtime/`. This skill must reuse the same helper CLI, configuration rules, and runtime references rather than duplicating setup logic or depending on the formalization entrypoint.

## Setup-Only Flow

1. Match the user's language by default; if ambiguous, default to Chinese.
2. Inspect tool and workspace readiness with `doctor` or `env`.
3. If `elan`, `lean`, or `lake` is missing, explain the required Lean installation step first. Install Lean through the official `elan` channel appropriate for the user's OS after approval; `lean` and `lake` should come from the `elan` toolchain rather than a repository-local copy.
4. Prefer an existing Lake project when the user points to one.
5. When creating an isolated test directory or workspace, suggest a safe default name and let the user confirm or rename it; use the default if the user has no naming preference.
6. For standalone future Lean work, create or reuse the canonical managed workspace `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` with the AI4Math managed baseline toolchain `leanprover/lean4:v4.28.0`.
7. Create the workspace only after explaining that Lean/mathlib artifacts may be downloaded or built. If the canonical workspace already exists and is complete, reuse it instead of rebuilding or downloading again.
8. Run the bundled smoke test after setup.
9. Report the installed tools, workspace path, Lean toolchain, mathlib revision when available, smoke-test result, and any remaining action.
10. After successful setup or smoke-test validation, do not end passively. Offer a short next-step menu and recommend one default next action.
11. Include an optional cross-platform IDE frontend path in that menu: identify the user's OS when needed, then guide them to install or verify VS Code with the Lean 4 extension on macOS, Windows, or Linux, open the verified Lake project or shared workspace, open a known passing `.lean` file, and confirm Lean InfoView is connected to the same toolchain that passed local validation.
12. If the user next wants formalization, proof repair, theorem transcription, `sorry` completion, patch review, or Numina proof search, hand off to `lean-formalization`.

## Post-Setup Guidance

Offer a short next-step menu after setup succeeds:

- inspect an existing Lean/Lake project;
- run or explain the built-in smoke theorem result;
- configure the VS Code / Lean 4 extension frontend for the verified project on macOS, Windows, or Linux, and confirm Lean InfoView works;
- repair a Lean file or complete `sorry`;
- formalize a natural-language or LaTeX theorem;
- continue setup-only validation if the user only wants environment readiness.

As a rule, mention optional Numina only when the user explicitly asks for the official Lean Agent, batch proof search, or an external backend adapter; do not make Numina or API keys part of the default next step.

## Commands

Resolve the helper from the shared runtime path `../lean-runtime/scripts/ai4m_lean.py`, then run it with `--cwd <target-project-or-workspace>`. In a source checkout this is the same helper under `skills/lean-runtime/scripts/ai4m_lean.py`.

```bash
python ../lean-runtime/scripts/ai4m_lean.py doctor --cwd <target-project-or-workspace>
python ../lean-runtime/scripts/ai4m_lean.py env --cwd <target-project-or-workspace>
python ../lean-runtime/scripts/ai4m_lean.py configure --cwd <target-project-or-workspace> --create-workspace
python ../lean-runtime/scripts/ai4m_lean.py smoke-test --cwd <target-project-or-workspace>
```

Use `--dry-run` before setup when the user wants to review commands.

## Boundaries

- Do not create a second setup implementation.
- Do not change a user project's `lean-toolchain` or mathlib revision without approval.
- Do not overwrite the canonical managed workspace for a different Lean/mathlib revision. Use `${AI4MATH_HOME:-~/.ai4math}/lean-workspaces/<version-key>/` only when the user explicitly needs a different standalone version.
- Do not require API keys for Lean/mathlib workspace setup.
- Do not require VS Code, Lean InfoView, or any IDE frontend for headless setup validation; offer it as a recommended human-facing follow-up after Lean/Lake readiness is confirmed.
- Do not configure or call official Numina unless the user explicitly asks for that optional backend.
- Do not commit machine-specific paths, downloaded runtime state, or secrets.

## References

- Read `../lean-runtime/references/lean_runtime_configuration.md` for shared workspace layout, local configuration, and version policy.
- Read `../lean-runtime/references/numina_runtime.md` only when the user asks for optional official Numina setup.
- Use `../lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests` for package validation.
