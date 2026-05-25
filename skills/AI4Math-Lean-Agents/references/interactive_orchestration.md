# Interactive Orchestration

The coordinating coding agent owns both user interaction and proof iteration. It does not delegate proof search to Numina, helper CLI commands, or any external backend.

This reference covers the guidance layer: session opening, intake, task classification, decomposition, direct Lean editing, result review, bounded iteration, and minimal failure handoff.

## Session Opening

Lead the interaction; do not wait for the user to drive every step. On a broad request, first orient to the current state instead of asking for every input at once:

- inspect whether the current directory is a Lake project;
- check whether the shared `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` exists;
- mention optional Numina readiness separately from direct Lean readiness;
- say what can be done immediately and what would require confirmation.

A language switch is not a task reset. Restate the current state in the user's language, keep the prior diagnosis, and continue with the recommended next action instead of returning to generic intake.

If no target is available, run or propose a safe local smoke/readiness check. Good examples are `lake env lean` against the shared workspace, `lake build` for the user's current Lake project when it is already present, or a helper `doctor` check when environment status is the question. Avoid ending with only "send me a file" or an equivalent passive handoff.

If no precise target is provided, offer a small menu and recommend one path. For example:

- repair or complete an existing Lean file;
- formalize a natural-language or LaTeX theorem;
- inspect a Lean/Lake project and summarize readiness;
- prepare the shared Lean workspace;
- discuss whether an official Numina run is appropriate.

Ask at most one blocking question at a time. A good opening ends with one decision question, not a checklist.

## Intake Questions

Ask only when not inferable:

- Is this repair, theorem formalization, proof completion, sorry completion, patch review, or batch work?
- What target file/folder and declaration should be used?
- Is changing the theorem statement allowed?
- Should standalone work use the reusable managed workspace?
- For natural-language or LaTeX input, what statement should be considered authoritative?

Prefer asking these only after orientation. If the repository already reveals the likely next step, state the recommendation and ask for confirmation.

## Decomposition

Break large requests into small Lean targets that can be checked with direct Lean/Lake commands or the optional helper `check` command.

For natural-language or LaTeX statements, draft the Lean declaration first and ask for confirmation before long proof work. Once the declaration is confirmed, treat statement preservation as a hard guardrail.

## Iteration Policy

Stop when:

- validation succeeds without `sorry`, `admit`, or new `axiom`;
- max local iterations are reached;
- Lean workspace setup is missing or broken;
- the remaining error requires a human mathematical decision;
- the only path forward would weaken the theorem statement without approval.

When stopping before success, reduce the problem to the smallest useful failing fragment. Use `minimize-failure` when it helps, then report exact Lean errors/goals and the next human decision needed.
