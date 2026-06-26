---
name: lean-formalization
description: Use for interactive Lean 4 formal verification by coding agents with reusable Lean/mathlib workspaces, theorem formalization, proof repair, sorry completion, patch review, optional official Numina subagent deployment/calls, and minimal failure handoff.
---

# Lean Formalization

Use this skill when the user wants a coding agent to do Lean 4 formalization, proof repair, theorem transcription, sorry completion, review of a Lean patch, or optional official Numina Lean Agent/subagent work.

This is a coding-agent-first Lean skill. The coding agent is the primary Lean worker. It reads and edits Lean files, runs Lean/Lake checks, diagnoses errors, preserves theorem statements, and iterates with the user. Default execution mode is coding-agent mode.

Official Numina is an optional deployable subagent backend. Keep the official Numina deployment/call path available for users who ask for the official Lean Agent, batch proof search, or an external subagent run. Use Numina when the user asks for the official Lean Agent, batch proof search, or an external subagent run.

Match the user's language by default. If the user's language is ambiguous, default to Chinese. If the user writes Chinese, respond in Chinese from the first turn unless they ask otherwise. A language switch is not a task reset. Keep the current environment state, prior diagnosis, and recommended next action, then continue leading in the new language.

Lead the interaction; do not wait for the user to drive every step. When the user's request is broad or underspecified, first orient yourself to the Lean project/workspace state, then propose the next useful action in plain language. Do not open with a passive "send me the file" checklist when you can inspect context or offer a concrete starting path.

If no target is available, run or propose a safe local smoke/readiness check. Use the bundled smoke test when no user target is available. Then recommend a default path, such as checking the shared Lean workspace, running the built-in smoke theorem, inspecting a Lean project, or checking Numina subagent readiness if the user wants that path. Avoid ending with only "send me a file" or an equivalent passive handoff.

The bundled CLI is a helper toolbox, not the workflow driver. Prefer normal coding-agent judgment, direct file edits, `rg`, Lean/Lake validation, and repository context. Use helper commands only when their deterministic output is useful.

Use official Numina through a human-in-the-loop subagent workflow. Numina lives under shared local state at `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/`; the coding agent explains clone, setup, API-key, proxy/MCP, and upstream runner implications before running setup or calling the official runner. Do not turn helper commands into a closed proof workflow.

Opening readiness should inspect local Lean readiness and Numina subagent readiness separately. Do not require API keys for the default coding-agent path. Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

Do not remove the official Numina subagent path. Treat it as an optional backend with explicit approval, while keeping the direct coding-agent Lean workflow useful without external APIs.

## Agent Playbook

1. Start by orienting the session: inspect the current repository/workspace when possible, distinguish existing Lake project, shared Lean workspace, local Lean validation readiness, Numina runtime, and Numina credentials/auth, and summarize what is already usable. Treat upstream Numina example projects as demos only; do not let their pinned `lean-toolchain` make the shared workspace look broken.
2. If the user has not provided a precise target, offer a small next-step menu such as run the bundled smoke test, repair an existing Lean file, formalize a natural-language/LaTeX theorem, inspect a Lean project, configure Numina credentials, run a Numina readiness check, or prepare the shared workspace as a Numina target. Recommend one default path based on what inspection found.
3. Ask at most one blocking question at a time. Prefer a concrete recommendation plus one decision question over a list of required inputs.
4. Understand the user's intent: direct coding-agent repair/formalization, configure Numina, call Numina, repair a file, formalize a statement, prove a target, complete `sorry`, review a patch, batch a folder, or minimize a failure.
5. Locate the relevant Lean project, files, declarations, imports, and current errors. Use the user's existing Lake project when available; otherwise use the shared workspace as the coding-agent project context and optional Numina target project.
6. For standalone files, use or create the shared workspace `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`; do not create a second project-local workspace unless the user asks for isolation.
7. When reporting readiness, lead with local Lean readiness, then Numina subagent readiness. If Numina credentials are missing, say that only the optional Numina subagent path needs configuration.
8. Before a Numina setup or run, inspect `doctor` readiness, explain the deployment/call, target project, prompt, result directory, credential/proxy/MCP state, and local validation plan; proceed only after approval.
9. For natural-language or LaTeX input, draft the Lean declaration and ask for confirmation before long proof work.
10. Edit Lean directly in small steps for the default coding-agent path. If Numina is approved, call the official Numina runner for proof search/formalization, then run Lean/Lake validation and patch safety checks before accepting results.
11. Preserve theorem statements unless the user explicitly approves a change.
12. Reject final patches that contain `sorry`, `admit`, or newly introduced `axiom`.
13. If blocked, stop cleanly with the smallest useful failing Lean fragment, exact errors/goals, and the next mathematical decision needed.

## Helper Toolbox

Use `python scripts/ai4m_lean.py <command>` when it saves effort or reduces risk:

- `env` / `doctor`: inspect Lean workspace, local tool availability, and Numina subagent readiness.
- `configure --create-workspace`: create or reuse the shared managed workspace.
- `configure --setup-numina --project-name <name>`: after user approval, clone/configure the official Numina runtime under `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/`.
- `smoke-test`: run the bundled `examples/smoke/NuminaSmoke.lean` target in the shared workspace without external API calls.
- `check`: run a structured Lean/Lake validation.
- `review` / `detect-sorry`: guard against placeholders, axioms, and statement drift.
- `minimize-failure`: extract a compact failing Lean fragment.
- `prove` / `formalize` / `repair` / `complete-sorries` / `batch`: optional dry-run task envelopes for coding-agent bookkeeping; use the official Numina runner only when the optional subagent path is approved.
- `verify-delivery`: validate this skill package.

All helper commands emit machine-readable JSON on stdout. Human-readable diagnostics go to stderr or log files.

## Numina Runtime

When using the official Numina runtime, follow `references/numina_runtime.md`. For auth/proxy/MCP/failure triage, follow `references/numina_subagent_troubleshooting.md`. Proof strategy is a human-in-the-loop process with the user, the coding agent, local Lean checks, and, when approved, the official Numina runner as an optional subagent backend.

## Safety Rules

- Do not call external model APIs or mutate Numina runtime state without approval.
- If the user asks for the official Lean Agent, Numina, batch proof search, or external subagent, explain needed credentials/setup directly.
- Do not commit local machine-specific paths.
- Do not call external APIs during `env`, `doctor`, `check`, `review`, `detect-sorry`, tests, or dry-runs.
- Do not store secrets in tracked files; use environment variables or `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/.env.local`.
- Do not accept final Lean patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Do not silently weaken theorem statements or change existing project versions.
- Do not let helper command availability override a better coding-agent path.
- Do not remove the official Numina subagent path.

## References

- Read `references/direct_lean_workflow.md` for the default coding-agent proof/repair/formalization loop.
- Read `references/lean_runtime_configuration.md` when setting up or diagnosing the reusable Lean workspace.
- Read `references/numina_runtime.md` when the user wants the official Numina deployment/call path.
- Read `references/numina_subagent_troubleshooting.md` when Numina auth, proxy, MCP, or runner failures appear.
- Read `references/interactive_orchestration.md` when guiding user intake and task decomposition.
- Read `references/review_checklist.md` before accepting a Lean patch.
- Read `references/failure_taxonomy.md` when reporting a blocked proof.
- Read `references/numina_reverse_analysis.md` when explaining which Numina mechanisms were distilled and which are delegated to the optional official runtime.
