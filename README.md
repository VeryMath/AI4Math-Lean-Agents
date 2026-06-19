# Lean Formalization

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

Lean Formalization is a guidance-first skill package for Lean 4 formal
verification with coding agents. The default Lean Agent path orchestrates the
official Numina Lean Agent runtime; local Lean editing is the validation and
fallback path when Numina is unavailable, declined, or insufficient. The bundled
CLI is only a deterministic helper toolbox for environment checks, Lean
validation, Numina readiness/setup, patch review, and minimal failure extraction.

The canonical skill package lives at:

```text
skills/lean-formalization/
```

## What This Skill Does

This standalone skill helps a coding agent work with Lean 4 formalization tasks:
inspect a Lean project, transcribe theorem statements, repair proofs, complete
`sorry`s when appropriate, review patches for unsafe proof shortcuts, and record
machine-checking evidence or a minimized failure.

Use it directly with a Lean project, a Lean file, or a theorem statement that you
want the agent to formalize or validate.

## Installation / Loading

Clone or open this skill repository in your coding-agent environment. Then ask
your coding agent to read:

```text
AGENTS.md
SKILL.md
skills/lean-formalization/SKILL.md
```

If your agent supports local Skill discovery, install or link
`skills/lean-formalization/` into that agent's Skill path and reload the agent
if needed. Platform notes live in `CLAUDE.md`, `GEMINI.md`,
`.codex/INSTALL.md`, and `.opencode/INSTALL.md`.

Codex-style local install example:

```bash
mkdir -p ~/.codex/skills
rsync -a --delete skills/lean-formalization/ ~/.codex/skills/lean-formalization/
```

## Quick Start

```text
Use this repository's Lean workflow.

Read:
- AGENTS.md
- SKILL.md
- skills/lean-formalization/SKILL.md

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
    └── lean-formalization/
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
python skills/lean-formalization/scripts/ai4m_lean.py env --cwd .
python skills/lean-formalization/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-formalization/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/lean-formalization/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
python skills/lean-formalization/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

The helper CLI is not the proof engine. The coding agent remains responsible for reading Lean errors, editing proofs, choosing proof strategy, and matching the user's language.

For the optional Numina path, read `skills/lean-formalization/references/numina_runtime.md`. Setup and official runner calls may clone repositories, install tools, or use external model/API credentials, so they should be explained before execution.

## Validate

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

For a full local Lean workspace check:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```
