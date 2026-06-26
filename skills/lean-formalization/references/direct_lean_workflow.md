# Direct Coding-Agent Lean Workflow

This is the default workflow. The coding agent reads and edits Lean directly, runs Lean/Lake checks, and iterates from concrete errors/goals. It distills Lean-specialist agent patterns into local work: theorem-state loops, premise retrieval, bounded proof attempts, failed-strategy memory, and minimal failure handoff. Official Numina remains available as an optional deployable subagent backend, but it is not required for ordinary Lean formalization, proof repair, or sorry completion.

## Guidance-First Loop

1. Read the user's request and classify whether this is repair, theorem formalization, proof completion, sorry completion, patch review, Numina setup/call, or output validation.
2. Inspect the target files, imports, nearby lemmas, and current Lean errors.
3. Choose the validation context: existing Lake project first, managed workspace only for standalone files.
4. For formalization, draft the Lean declaration and ask for confirmation before long proof work.
5. Build a compact local context pack from current goals, nearby proofs, relevant declarations, and failed attempts.
6. Make one small Lean edit at a time.
7. Run Lean/Lake validation after meaningful edits, usually `lake env lean <file>`, `lake build`, or the helper `check` command.
8. Diagnose the first concrete Lean error or unsolved goal before changing strategy.
9. Search before inventing: use existing imports, nearby lemmas, and project/mathlib declarations before adding helper lemmas.
10. Add helper lemmas only when they reduce proof complexity and keep theorem statements unchanged.
11. Review the final patch with direct inspection and, when useful, `review` or `detect-sorry`.
12. If blocked, use direct reduction and/or `minimize-failure` to return the smallest failing Lean fragment plus exact errors/goals and tried routes.

## When to Use Helpers

Use helpers for mechanical checks:

- environment and workspace readiness: `env`, `doctor`, `configure`;
- validation: `check`;
- safety guards: `review`, `detect-sorry`;
- failure handoff: `minimize-failure`;
- package QA: `verify-delivery`.

Do not route creative proof search through helper commands. `prove`, `formalize`, `repair`, `complete-sorries`, and `batch` only produce optional task envelopes for bookkeeping. Use the official Numina runner only when the optional subagent path is approved.

## Workspace Choice

Prefer a user's existing Lake project when the target file is inside one. For standalone `.lean` files, use the reusable `${AI4MATH_HOME:-~/.ai4math}/lean-workspace` so Lean, Lake, and mathlib artifacts are shared across tasks and projects.

When a user project has its own `lean-toolchain` and mathlib revision, keep those versions unless the user explicitly approves a change. When creating a managed workspace, use the configured preferred toolchain or `auto`.

## Good Stopping Points

Stop with success when the relevant Lean file or project validates and no unsafe placeholders remain.

Stop with a minimal failure when:

- the remaining proof step requires a human mathematical decision;
- the theorem statement appears ambiguous or unconfirmed;
- progress would require weakening a statement without approval;
- repeated local attempts are cycling over the same Lean error.
