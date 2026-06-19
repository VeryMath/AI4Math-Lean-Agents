---
name: lean-formalization
description: Use for interactive Lean 4 formal verification through the official Numina Lean Agent runtime, reusable Lean/mathlib workspaces, Numina deployment/calls, theorem formalization, proof repair, sorry completion, patch review, and minimal failure handoff.
---

# Lean Formalization

Use this skill when the user wants Lean 4 formalization, proof repair, theorem transcription, sorry completion, review of a Lean patch, or a Lean Agent run.

In this skill, Lean Agent means the official Numina Lean Agent runtime. Default execution mode is Numina Agent mode. The coding agent orchestrates Numina deployment, configuration, invocation, and local Lean validation. Do not redefine Lean Agent as the coding agent.

Match the user's language by default. If the user's language is ambiguous, default to Chinese. If the user writes Chinese, respond in Chinese from the first turn unless they ask otherwise. A language switch is not a task reset. Keep the current environment state, prior diagnosis, and recommended next action, then continue leading in the new language.

Lead the interaction; do not wait for the user to drive every step. When the user's request is broad or underspecified, first orient yourself to the Lean project/workspace state, then propose the next useful action in plain language. Do not open with a passive "send me the file" checklist when you can inspect context or offer a concrete starting path.

If no target is available, run or propose a safe local smoke/readiness check. Use the bundled smoke test when no user target is available. Then recommend a default path, such as checking Numina readiness, preparing the shared workspace as Numina's target project, or running the built-in smoke theorem before an official Numina call. Avoid ending with only "send me a file" or an equivalent passive handoff.

The bundled CLI is a helper toolbox, not the workflow driver. Prefer normal coding-agent judgment, `rg`, Lean/Lake validation, repository context, and the official Numina runner. Use helper commands only when their deterministic output is useful.

Use official Numina through a human-in-the-loop runtime workflow. Numina lives under shared local state at `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/`; the coding agent explains clone, setup, API-key, and upstream runner implications before running setup or calling the official runner. Do not turn helper commands into a closed proof workflow.

Opening readiness should inspect Numina readiness before recommending work. Do not say API keys are unnecessary until the Numina mode is clear. Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

Direct Lean editing is a validation and fallback path, not the default Lean Agent mode. Use it to check the shared workspace, validate Numina output, reduce failures, or continue locally only when the user declines or cannot use Numina.

## Agent Playbook

1. Start by orienting the session: inspect the current repository/workspace when possible, distinguish existing Lake project, shared Lean workspace, Numina runtime, and Numina credentials/auth, and summarize what is already usable. Treat upstream Numina example projects as demos only; do not let their pinned `lean-toolchain` make the shared workspace look broken.
2. If the user has not provided a precise target, offer a small next-step menu such as configure Numina credentials, run a Numina readiness check, prepare the shared workspace as a Numina target, formalize a natural-language/LaTeX theorem through Numina, repair an existing Lean file through Numina, or inspect a Lean project. Recommend one default path based on what inspection found.
3. Ask at most one blocking question at a time. Prefer a concrete recommendation plus one decision question over a list of required inputs.
4. Understand the user's intent: configure Numina, call Numina, repair a file, formalize a statement, prove a target, complete `sorry`, review a patch, batch a folder, or minimize a failure.
5. Locate the relevant Lean project, files, declarations, imports, and current errors. Use the user's existing Lake project when available; otherwise use the shared workspace as Numina's target project.
6. For standalone files, use or create the shared workspace `${AI4MATH_HOME:-~/.ai4math}/lean-workspace`; do not create a second project-local workspace unless the user asks for isolation.
7. When reporting readiness, lead with Numina readiness, then local Lean validation readiness. If Numina credentials are missing, say that Numina calls need configuration instead of implying the skill can proceed as the expected Lean Agent.
8. Before a Numina setup or run, inspect `doctor` readiness, explain the deployment/call, target project, prompt, result directory, credential state, and local validation plan; proceed only after approval.
9. For natural-language or LaTeX input, draft the Lean declaration and ask for confirmation before long proof work.
10. Call the official Numina runner for proof search/formalization when approved. After Numina changes Lean files, run Lean/Lake validation and patch safety checks before accepting results.
11. Preserve theorem statements unless the user explicitly approves a change.
12. Reject final patches that contain `sorry`, `admit`, or newly introduced `axiom`.
13. If blocked, stop cleanly with the smallest useful failing Lean fragment, exact errors/goals, and the next mathematical decision needed.

## Helper Toolbox

Use `python scripts/ai4m_lean.py <command>` when it saves effort or reduces risk:

- `env` / `doctor`: inspect Lean workspace, local tool availability, and Numina readiness.
- `configure --create-workspace`: create or reuse the shared managed workspace.
- `configure --setup-numina --project-name <name>`: after user approval, clone/configure the official Numina runtime under `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/`.
- `smoke-test`: run the bundled `examples/smoke/NuminaSmoke.lean` target in the shared workspace without external API calls.
- `check`: run a structured Lean/Lake validation.
- `review` / `detect-sorry`: guard against placeholders, axioms, and statement drift.
- `minimize-failure`: extract a compact failing Lean fragment.
- `prove` / `formalize` / `repair` / `complete-sorries` / `batch`: optional dry-run task envelopes for bookkeeping; prefer the official Numina runner for actual Lean Agent proof search.
- `verify-delivery`: validate this skill package.

All helper commands emit machine-readable JSON on stdout. Human-readable diagnostics go to stderr or log files.

## Numina Runtime

When using the official Numina runtime, follow `references/numina_runtime.md`. Proof strategy is a human-in-the-loop process with the user, the coding agent, local Lean checks, and the official Numina runner as the default Lean Agent.

## Safety Rules

- Do not call external model APIs or mutate Numina runtime state without approval.
- If the user asks for the Lean Agent, treat that as Numina and explain any needed credentials/setup directly.
- Do not commit local machine-specific paths.
- Do not call external APIs during `env`, `doctor`, `check`, `review`, `detect-sorry`, tests, or dry-runs.
- Do not store secrets in tracked files; use environment variables or `${AI4MATH_HOME:-~/.ai4math}/numina-runtime/.env.local`.
- Do not accept final Lean patches containing `sorry`, `admit`, or newly introduced `axiom`.
- Do not silently weaken theorem statements or change existing project versions.
- Do not let helper command availability override the official Numina Agent path when the user expects Lean Agent behavior.

## References

- Read `references/direct_lean_workflow.md` for local Lean validation and fallback repair guidance.
- Read `references/lean_runtime_configuration.md` when setting up or diagnosing the reusable Lean workspace.
- Read `references/numina_runtime.md` when the user wants the official Numina deployment/call path.
- Read `references/interactive_orchestration.md` when guiding user intake and task decomposition.
- Read `references/review_checklist.md` before accepting a Lean patch.
- Read `references/failure_taxonomy.md` when reporting a blocked proof.
- Read `references/numina_reverse_analysis.md` when explaining which Numina mechanisms were distilled and which are delegated to the optional official runtime.
