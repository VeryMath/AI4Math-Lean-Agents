# Interactive Orchestration

The coordinating coding agent owns both user interaction and proof iteration. It does not delegate proof search to Numina, helper CLI commands, or any external backend.

This reference covers the guidance layer: intake, task classification, decomposition, direct Lean editing, result review, bounded iteration, and minimal failure handoff.

## Intake Questions

Ask only when not inferable:

- Is this repair, theorem formalization, proof completion, sorry completion, patch review, or batch work?
- What target file/folder and declaration should be used?
- Is changing the theorem statement allowed?
- Should standalone work use the reusable managed workspace?
- For natural-language or LaTeX input, what statement should be considered authoritative?

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
