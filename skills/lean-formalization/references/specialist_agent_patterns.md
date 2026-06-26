# Lean-Specialist Agent Pattern Distillation

This reference explains how the coding-agent-first skill absorbs Lean-specialist agent designs without making any external agent mandatory. Preserve the mechanism, not prompts, benchmark-specific assumptions, or private implementation details.

## Source Families

- Numina-style coding-agent orchestration: project setup, official runner calls, Claude/MCP/tool integration, bounded external proof attempts, and local Lean validation.
- LeanDojo/ReProver-style loops: theorem state as the central object, premise retrieval, tactic generation, execution feedback, and proof search evaluation.
- LeanCopilot-style assistance: programmatic tactic, premise, and proof-search hooks that a human/coding agent can treat as optional suggestions.
- COPRA-style proof search: stateful attempts, backtracking, failed-strategy memory, and compact proof-state reporting.
- Lean LSP/MCP-style integration: editor/server feedback, goal inspection, diagnostics, and tool scope tied to the target project.
- Lightweight iterative agents: small edit/check loops, local context retrieval, and explicit stop conditions.

These sources are patterns to distill. Do not claim parity with a specialist prover unless the original backend is actually called and validated.

Public source anchors:

- Numina Lean Agent: `https://github.com/project-numina/numina-lean-agent`
- LeanDojo/ReProver: `https://github.com/lean-dojo/LeanDojo`
- LeanCopilot: `https://github.com/lean-dojo/LeanCopilot`
- COPRA: `https://github.com/trishullab/copra`

## Distilled Default Workflow

1. Gate the project: identify the Lake root, toolchain, mathlib revision, imports, and build status before proof work.
2. Normalize the target: locate the authoritative theorem statement, declaration name, hypotheses, namespace, and allowed statement changes.
3. Build a local context pack: nearby lemmas, imported modules, relevant declarations from `rg`, current goals, and prior failed attempts.
4. Run the theorem-state loop: make one small edit, run Lean, read the first concrete error or goal, update the context pack, and continue.
5. Use bounded search: try a small number of plausible tactic/proof routes; record failed routes so the agent does not cycle.
6. Retrieve before inventing: search existing project/mathlib names and nearby proofs before adding helper lemmas.
7. Validate as oracle: Lean/Lake success is required; final patches must not contain `sorry`, `admit`, new `axiom`, or unapproved statement drift.
8. Escalate deliberately: call optional Numina or another specialist backend only after explaining target, credentials/proxy/MCP state, result directory, and validation plan.
9. Hand off minimally: when blocked, return the smallest failing Lean fragment, exact goals/errors, tried routes, and the next mathematical decision.

## Pattern Map

| Specialist mechanism | Coding-agent integration |
| --- | --- |
| Runtime/environment gate | `env`, `doctor`, `configure`, direct Lake root inspection |
| Theorem-state centered search | Lean error/goal loop after each small edit |
| Premise retrieval | `rg`, nearby imports/proofs, project declarations, optional external search |
| Bounded proof attempts | `max_rounds`, local iteration caps, failed-strategy notes |
| Backtracking/failure memory | Record tried tactic families and rejected statement changes |
| External proof backend | Optional official Numina subagent, never required for default work |
| Validation oracle | Lean/Lake plus `review` and `detect-sorry` |
| Failure artifact | `minimize-failure` and exact errors/goals |

## Escalation Rule

Default to distilled local patterns. Escalate to a real specialist backend only when:

- the user asks for Numina, official Lean Agent, batch proof search, or an external subagent;
- local bounded attempts are cycling and the user approves a backend call;
- the required credentials, proxy, MCP scope, and target project are understood;
- all backend output will still be reviewed and checked locally.

## Anti-Patterns

- Do not replace proof work with a CLI workflow that only asks the user for more input.
- Do not treat a missing Numina key as blocking ordinary coding-agent Lean work.
- Do not copy upstream prompts or claim hidden benchmark behavior.
- Do not add helper lemmas or theorem statement changes just to make a proof easier unless the user approves.
- Do not let an external backend output bypass local Lean validation and patch review.
