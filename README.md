<div align="center">

# AI4Math · Lean Agents

Lean 4 setup, formalization, proof repair, patch review, and optional Numina
subagent workflows for coding agents.

[中文说明](README.zh-CN.md) · [Skill packages](#skill-packages) · [Quick start](#quick-start) · [Security model](#security-and-scope)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-2-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

## What This Repository Is

This repository is the AI4Math home for Lean-agent skills. It provides one
setup-only entrypoint and one formalization entrypoint so a coding agent can
inspect Lean projects, prepare reusable mathlib workspaces, repair proofs, and
validate final patches with evidence.

`lean-formalization` incorporates public Lean-specialist agent patterns such as
theorem-state loops, premise retrieval, bounded proof search, validation gates,
failure memory, and optional official Numina handoff. These patterns are treated
as workflow mechanisms, not mandatory external services.

## Skill Packages

| Package | Use it for | Start here |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | Install or verify Lean 4, `elan`, `lake`, and reusable mathlib workspace readiness before proof work. | [`README`](skills/lean-setup/README.md) · [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | Formalize theorem statements, repair Lean proofs, complete `sorry`, review patches, and optionally coordinate Numina runs. | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

## Quick Start

Clone the repository and choose the entrypoint:

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
```

For environment setup only, start with:

```text
skills/lean-setup/SKILL.md
```

For formalization or proof repair, start with:

```text
skills/lean-formalization/SKILL.md
```

## Repository Layout

```text
AI4Math-Lean-Agents/
├── README.md
├── README.zh-CN.md
├── SKILL.md
└── skills/
    ├── lean-setup/
    └── lean-formalization/
```

The root `SKILL.md` is a compatibility router. Package-local instructions are
the source of truth for concrete Lean work.

## Validation

Use package-local validation when changing Lean logic. The formalization package
provides the helper:

```bash
python skills/lean-formalization/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

At minimum, run the local skill validator on each changed standard skill
package and check README links.

## Security and Scope

Do not commit Lean build artifacts, downloaded Numina runtime state, API keys,
`.env` files, machine-specific paths, or private theorem notes. Do not present
proofs as accepted without local Lean/Lake validation or an explicit approved
review gate.
