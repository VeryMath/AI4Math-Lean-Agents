# Lean Formalization

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

`lean-formalization` helps a coding agent work with Lean 4 formalization, proof repair, and validation tasks.

## When To Use It

Use this skill when you have:

- a Lean project or Lean file that needs inspection;
- a theorem statement to transcribe or formalize;
- a proof with `sorry`, `admit`, errors, or statement drift risk;
- a need for optional Numina setup mediated by the coding agent.

## What It Produces

The agent should produce Lean patches, validation summaries, blocked-goal explanations, minimized failures, and optional Numina setup evidence.

## Installation

Copy this to your coding agent:

```text
Please install the `lean-formalization` skill from https://github.com/VeryMath/AI4Math-Lean-Agents.git (branch: feature/numina-runtime-delivery). Read `.agent.md`, install the declared Skill entrypoint, verify that `$lean-formalization` is discoverable, and tell me whether I need to restart the agent.
```

If you already have this skill repository locally, replace the repository URL
with the local folder path. The coding agent should handle cloning, linking,
configuration, reload/restart checks, and verification.

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
