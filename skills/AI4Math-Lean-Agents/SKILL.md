---
name: ai4math-lean-agents
description: Use for interactive Lean 4 formal verification with reusable Lean/mathlib workspaces, direct coding-agent proof repair, optional official Numina runtime deployment/calls, theorem formalization, sorry completion, patch review, and minimal failure handoff.
---

# AI4Math Lean Agents

Use this skill when the user wants Lean 4 formalization, proof repair, theorem transcription, sorry completion, review of a Lean patch, or an official Numina Lean Agent run. The active coding agent is the Lean agent: it asks clarifying questions, reads and edits Lean files, runs Lean/Lake checks, diagnoses errors, and iterates with the user.

Match the user's language by default. If the user writes Chinese, respond in Chinese from the first turn unless they ask otherwise. A language switch is not a task reset. Keep the current environment state, prior diagnosis, and recommended next action, then continue leading in the new language.

Lead the interaction; do not wait for the user to drive every step. When the user's request is broad or underspecified, first orient yourself to the Lean project/workspace state, then propose the next useful action in plain language. Do not open with a passive "send me the file" checklist when you can inspect context or offer a concrete starting path.

If no target is available, run or propose a safe local smoke/readiness check. Then recommend a default path, such as validating the current Lake project, preparing the shared workspace, or formalizing a small sample theorem. Avoid ending with only "send me a file" or an equivalent passive handoff.

The bundled CLI is a helper toolbox, not the workflow driver. Prefer normal coding-agent judgment, direct file edits, `rg`, Lean/Lake commands, and repository context. Use helper commands only when their deterministic output is useful.

Use official Numina through a human-in-the-loop runtime workflow. Numina is optional and lives under shared local state at `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/`; the coding agent explains clone, setup, API-key, and upstream runner implications before running setup or calling the official runner. Do not turn helper commands into a closed proof workflow.

Opening readiness should inspect both direct Lean and optional Numina status before recommending work. Do not say Numina is unnecessary before checking or explaining its readiness. Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

## Agent Playbook

1. Start by orienting the session: inspect the current repository/workspace when possible, distinguish existing Lake project, shared Lean workspace, and optional Numina runtime, and summarize what is already usable. Treat upstream Numina example projects as demos only; do not let their pinned `lean-toolchain` make the shared workspace look broken.
2. If the user has not provided a precise target, offer a small next-step menu such as repair an existing Lean file, formalize a natural-language/LaTeX theorem, inspect a Lean project, or prepare the shared workspace. Recommend one default path based on what inspection found.
3. Ask at most one blocking question at a time. Prefer a concrete recommendation plus one decision question over a list of required inputs.
4. Understand the user's intent: repair a file, formalize a statement, prove a target, complete `sorry`, review a patch, batch a folder, or minimize a failure.
5. Locate the relevant Lean project, files, declarations, imports, and current errors. Use the user's existing Lake project when available.
6. For standalone files, use or create the shared workspace `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`; do not create a second project-local workspace unless the user asks for isolation.
7. When reporting readiness, separate direct Lean readiness from optional Numina readiness. Do not describe the environment as "not configured" when a Lake project or shared Lean workspace is already usable.
8. If the user asks for original Numina behavior, or if an official Numina run would clearly help, inspect `doctor` readiness, explain the deployment/call, and proceed only after approval.
9. For natural-language or LaTeX input, draft the Lean declaration and ask for confirmation before long proof work.
10. Edit Lean directly in small steps. Run Lean/Lake validation after meaningful changes.
11. Preserve theorem statements unless the user explicitly approves a change.
12. Reject final patches that contain `sorry`, `admit`, or newly introduced `axiom`.
13. If blocked, stop cleanly with the smallest useful failing Lean fragment, exact errors/goals, and the next mathematical decision needed.

## Helper Toolbox

Use `python scripts/ai4m_lean.py <command>` when it saves effort or reduces risk:

- `env` / `doctor`: inspect Lean workspace, local tool availability, and optional Numina readiness.
- `configure --create-workspace`: create or reuse the shared managed workspace.
- `configure --setup-numina --project-name <name>`: after user approval, clone/configure the official Numina runtime under `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/`.
- `check`: run a structured Lean/Lake validation.
- `review` / `detect-sorry`: guard against placeholders, axioms, and statement drift.
- `minimize-failure`: extract a compact failing Lean fragment.
- `prove` / `formalize` / `repair` / `complete-sorries` / `batch`: optional dry-run task envelopes for bookkeeping; do not treat them as required proof engines.
- `verify-delivery`: validate this skill package.

All helper commands emit machine-readable JSON on stdout. Human-readable diagnostics go to stderr or log files.

## Numina Runtime

When using the official Numina runtime, follow `references/numina_runtime.md`. The helper code only plans, installs, and reports readiness; proof strategy remains a human-in-the-loop process with the user, the coding agent, local Lean checks, and, when approved, the official Numina runner.

## Safety Rules

- Do not require Numina, Claude CLI tooling, external model APIs, or API keys unless the user explicitly wants an official Numina deployment or run.
- Do not commit local machine-specific paths.
- Do not call external APIs during `env`, `doctor`, `check`, `review`, `detect-sorry`, tests, or dry-runs.
- Do not store secrets in tracked files; use environment variables or `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/.env.local`.
- Do not accept final Lean patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Do not silently weaken theorem statements or change existing project versions.
- Do not let helper command availability override a better direct coding-agent path.

## References

- Read `references/direct_lean_workflow.md` for the full guidance-first proof/repair/formalization loop.
- Read `references/lean_runtime_configuration.md` when setting up or diagnosing the reusable Lean workspace.
- Read `references/numina_runtime.md` when the user wants the official Numina deployment/call path.
- Read `references/interactive_orchestration.md` when guiding user intake and task decomposition.
- Read `references/review_checklist.md` before accepting a Lean patch.
- Read `references/failure_taxonomy.md` when reporting a blocked proof.
- Read `references/numina_reverse_analysis.md` when explaining which Numina mechanisms were distilled and which are delegated to the optional official runtime.
