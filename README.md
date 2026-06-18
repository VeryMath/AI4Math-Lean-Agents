# AI4Math Lean Agents

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

AI4Math Lean Agents is a guidance-first skill package for Lean 4 formal
verification with coding agents. The default Lean Agent path orchestrates the
official Numina Lean Agent runtime; local Lean editing is the validation and
fallback path when Numina is unavailable, declined, or insufficient. The bundled
CLI is only a deterministic helper toolbox for environment checks, Lean
validation, Numina readiness/setup, patch review, and minimal failure handoff.

The canonical skill package lives at:

```text
skills/AI4Math-Lean-Agents/
```

## AI4Math Role

This skill is the Lean 4 formalization and proof-repair layer in the AI4Math
stack. Use it when a theorem statement, proof obligation, or generated proof
candidate needs machine-checked Lean evidence rather than informal proof review.

## Handoff

Upstream inputs may come from `agentic-rethlas-proving`,
`discover-math-problems`, `paper-to-skill`, or a user Lean project. Handoff
artifacts should include the intended theorem statement, allowed assumptions,
imports, current Lean errors or goals, and any proof blueprint. Return validated
Lean patches, minimized failures, or blocked proof obligations without changing
the theorem statement unless the user approves.

## Installation / Loading

Use the repository checkout first. Ask your coding agent to read:

```text
AGENTS.md
SKILL.md
skills/AI4Math-Lean-Agents/SKILL.md
```

If your agent supports local Skill discovery, install or link
`skills/AI4Math-Lean-Agents/` into that agent's Skill path and reload the agent
if needed. Platform notes live in `CLAUDE.md`, `GEMINI.md`,
`.codex/INSTALL.md`, and `.opencode/INSTALL.md`.

Codex-style local install example:

```bash
mkdir -p ~/.codex/skills
rsync -a --delete skills/AI4Math-Lean-Agents/ ~/.codex/skills/ai4math-lean-agents/
```

## Quick Start

```text
Use this repository's Lean workflow.

Read:
- AGENTS.md
- SKILL.md
- skills/AI4Math-Lean-Agents/SKILL.md

Goal:
<describe the Lean formalization, repair, transcription, or validation task>

Constraints:
- inspect the Lean project first;
- preserve theorem statements unless approved;
- ask before Numina setup, source edits, or final proof claims.
```

## What It Supports

- Lean project/workspace inspection.
- Reusable shared `~/.ai4math/lean-workspace` setup for standalone Lean files.
- Theorem formalization, proof repair, proof completion, and `sorry` completion.
- Patch review for `sorry`, `admit`, newly introduced `axiom`, and theorem statement drift.
- Minimal failing Lean fragment extraction when a proof is blocked.
- Optional official `project-numina/numina-lean-agent` deployment/call flow, mediated by the coding agent.

Numina is optional. The public CLI does not expose a parallel `numina-*` workflow; `doctor` reports readiness and `configure --setup-numina --project-name <name>` performs the reviewed local setup under `~/.ai4math/numina-runtime/` by default.

## Repository Layout

```text
.
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── README.md
├── LICENSE
├── .github/
├── .cursor/             # optional Cursor rule
├── .opencode/           # optional OpenCode agent
└── skills/
    └── AI4Math-Lean-Agents/
        ├── SKILL.md
        ├── agents/
        ├── config/
        ├── prompts/
        ├── references/
        ├── schemas/
        ├── scripts/
        └── tests/
```

## How To Interact

Use a checkpoint loop:

```text
Lean task -> project inspection -> plan -> approve / revise / reject / skip
          -> approved edit or validation -> evidence summary -> next checkpoint
```

Use `approve` to run a proposed step, `revise` to update the plan, `reject` to
stop the path, and `skip` to move past a phase. The agent should ask before
theorem statement changes, optional Numina setup, source edits, or final proof
claims.

## Helper Commands

Run commands from the repository root:

```bash
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py env --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py doctor --cwd .
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

The helper CLI is not the proof engine. The coding agent remains responsible for reading Lean errors, editing proofs, choosing proof strategy, and matching the user's language.

For the optional Numina path, read `skills/AI4Math-Lean-Agents/references/numina_runtime.md`. Setup and official runner calls may clone repositories, install tools, or use external model/API credentials, so they should be explained before execution.

## Validate

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

For a full local Lean workspace check:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/AI4Math-Lean-Agents/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```
