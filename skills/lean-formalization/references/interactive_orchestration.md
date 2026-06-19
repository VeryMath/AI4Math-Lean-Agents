# Interactive Orchestration

The coordinating coding agent owns user interaction, Numina orchestration, and final validation. It delegates proof search/formalization to the official Numina Lean Agent by default when the user asks for the Lean Agent.

This reference covers the guidance layer: session opening, intake, task classification, Numina deployment/calls, local Lean validation, result review, bounded iteration, and minimal failure handoff.

## Session Opening

If the user's language is ambiguous, default to Chinese. The skill display name, repository name, or command name is not enough evidence to choose English.

In this skill, Lean Agent means the official Numina Lean Agent runtime. Default execution mode is Numina Agent mode. Do not redefine Lean Agent as the coding agent.

Lead the interaction; do not wait for the user to drive every step. On a broad request, first orient to the current state instead of asking for every input at once:

- inspect whether the current directory is a Lake project;
- check whether the shared `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` exists;
- inspect Numina runtime, upstream checkout, tools, and credential/auth readiness;
- mention local Lean readiness as the validation layer;
- say what can be done immediately and what would require confirmation.

Opening readiness should inspect Numina readiness before recommending work. Do not say API keys are unnecessary until the Numina mode is clear. Shared workspace is the default Lean project context; Numina may target it instead of upstream examples.

When checking Numina, distinguish runtime readiness from upstream demo readiness. The runtime can be usable with the shared Lean workspace even if an upstream example or benchmark pins a different `lean-toolchain`. Report that as an example-project issue, not as a failure of the shared environment.

A language switch is not a task reset. Restate the current state in the user's language, keep the prior diagnosis, and continue with the recommended next action instead of returning to generic intake.

If no target is available, run or propose a safe local smoke/readiness check. Use the bundled smoke test when no user target is available. Good examples are `smoke-test` against `examples/smoke/NuminaSmoke.lean`, `lake build` for the user's current Lake project when it is already present, or a helper `doctor` check when environment status is the question. Avoid ending with only "send me a file" or an equivalent passive handoff.

If no precise target is provided, offer a small menu and recommend one path. For example:

- configure missing Numina credentials/auth;
- run a Numina readiness check;
- run the bundled smoke test to verify the local Lean/mathlib validation layer;
- prepare the shared workspace as the Numina target project;
- call Numina on a natural-language/LaTeX theorem or Lean file;
- inspect a Lean/Lake project and summarize whether Numina can target it.

Ask at most one blocking question at a time. A good opening ends with one decision question, not a checklist.

## Intake Questions

Ask only when not inferable:

- Is this repair, theorem formalization, proof completion, sorry completion, patch review, or batch work?
- What target file/folder and declaration should be used?
- Is changing the theorem statement allowed?
- Should standalone work use the reusable managed workspace?
- Should we configure/call Numina now, or only inspect readiness?
- For natural-language or LaTeX input, what statement should be considered authoritative?

Prefer asking these only after orientation. If the repository already reveals the likely next step, state the recommendation and ask for confirmation.

## Decomposition

Break large requests into small Lean targets that Numina can run against and that can be checked afterward with Lean/Lake commands or the helper `check` command.

For natural-language or LaTeX statements, draft the Lean declaration first and ask for confirmation before long proof work. Once the declaration is confirmed, treat statement preservation as a hard guardrail.

## Numina Run

Before an official Numina call, state the target project/file, prompt file, max rounds, result directory, credential state, and validation plan. Ask for approval before any external model call or runtime mutation.

After Numina returns, inspect changed Lean files, run local Lean/Lake validation, and reject results containing `sorry`, `admit`, new `axiom`, or unapproved theorem statement changes.

## Iteration Policy

Stop when:

- validation succeeds without `sorry`, `admit`, or new `axiom`;
- max local iterations are reached;
- Lean workspace setup is missing or broken;
- Numina credentials/auth are missing and the user has not approved fallback work;
- the remaining error requires a human mathematical decision;
- the only path forward would weaken the theorem statement without approval.

When stopping before success, reduce the problem to the smallest useful failing fragment. Use `minimize-failure` when it helps, then report exact Lean errors/goals and the next human decision needed.
