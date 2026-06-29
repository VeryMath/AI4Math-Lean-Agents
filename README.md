<div align="center">

# AI4Math · Lean Agents

Lean 4 setup, formalization, proof repair, patch review, and optional
Lean-specialist backend workflows for coding agents.

[中文说明](README.zh-CN.md) · [Contributors](CONTRIBUTORS.md) · [Skill packages](#skill-packages) · [Installation](#installation) · [Quick start](#quick-start) · [Security model](#security-and-scope)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-2-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

## What This Repository Is

This repository is the AI4Math home for Lean-agent skills. It provides one
setup-only entrypoint and one formalization entrypoint so a coding agent can
inspect Lean projects, prepare reusable mathlib workspaces, repair proofs, and
validate final patches with evidence.

Both public entrypoints share the bundled `skills/lean-runtime/` support layer
for helper scripts, references, prompts, schemas, examples, and tests. Users
invoke only `lean-setup` or `lean-formalization`; installers should keep
`lean-runtime` next to them.

`lean-formalization` incorporates public Lean-specialist agent patterns such as
theorem-state loops, premise retrieval, bounded proof search, validation gates,
failure memory, and optional official Numina handoff. These patterns are treated
as workflow mechanisms, not mandatory external services. The optional Lean-specialist backend
path is explicit: official Numina is the currently supported optional deployable
backend; other backends remain future adapters until setup, call, validation,
and failure-triage contracts are documented.

Currently supported optional backend: official Numina Lean Agent runtime.
Future backend adapters do not claim support until deployment, readiness checks, invocation, validation, and failure triage are documented.

## Skill Packages

| Package | Use it for | Start here |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | Install or verify Lean 4, `elan`, `lake`, and reusable mathlib workspace readiness before proof work. | [`README`](skills/lean-setup/README.md) · [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | Formalize theorem statements, repair Lean proofs, complete `sorry`, review patches, and optionally coordinate Numina runs. | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

`skills/lean-runtime/` is a shared implementation layer, not a user-facing skill.

## Installation

The recommended path is AI-assisted installation: ask your coding agent to clone or update this repository, read the Skill instructions, install the entrypoints, and verify discovery.

```text
Please install these AI4Math Skills for me.

Repository: https://github.com/VeryMath/AI4Math-Lean-Agents.git
Branch: main
Skill paths:
- skills/lean-setup
- skills/lean-formalization

Steps:
1. Clone or update the repository locally.
2. Read README.md, SKILL.md, AGENTS.md if present, and each target Skill entrypoint.
3. If this environment supports local Skill discovery, link each directory that contains SKILL.md into the local skills directory.
4. Keep shared sibling support directories in place when a Skill depends on them.
5. Verify that the installed Skills are discoverable.
6. Tell me the installed paths, whether a restart is needed, and give me one test prompt.
```

For Lean skills, keep `skills/lean-runtime` installed as a sibling support directory. It is not a public entrypoint, but `lean-setup` and `lean-formalization` depend on it.

Manual fallback for Codex-style local discovery:

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/lean-setup" ~/.codex/skills/lean-setup
ln -s "$PWD/skills/lean-formalization" ~/.codex/skills/lean-formalization
ln -s "$PWD/skills/lean-runtime" ~/.codex/skills/lean-runtime
```

If your agent uses a different local Skill directory, replace `~/.codex/skills` with that configured path.

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

## Supported Scope

- Lean project/workspace inspection.
- Reusable shared `~/.ai4math/lean-workspace` setup for standalone Lean files, using the AI4Math managed baseline `leanprover/lean4:v4.28.0` unless explicitly overridden.
- Theorem formalization, proof repair, proof completion, and `sorry` completion.
- Patch review for `sorry`, `admit`, newly introduced `axiom`, and theorem statement drift.
- Minimal failing Lean fragment extraction when a proof is blocked.
- Related-work-informed Lean-specialist patterns: theorem-state loops, premise retrieval, bounded proof search, failure memory, validation oracles, and minimal handoff.
- Optional Lean-specialist backend adapter flow, currently implemented for official `project-numina/numina-lean-agent` deployment/calls mediated by the coding agent.

Numina is optional and is the only built-in deployable backend adapter. The public CLI does not expose a parallel `numina-*` workflow; `doctor` reports readiness and `configure --setup-numina --project-name <name>` performs the reviewed local setup under `~/.ai4math/numina-runtime/` by default.

Future backend adapters can follow `skills/lean-runtime/references/backend_adapter_checklist.md`, but should not be described as supported until deployment, readiness checks, invocation, validation, and failure triage are documented.

## Repository Layout

```text
AI4Math-Lean-Agents/
├── README.md
├── README.zh-CN.md
├── SKILL.md
└── skills/
    ├── lean-setup/
    ├── lean-formalization/
    └── lean-runtime/
```

The root `SKILL.md` is a compatibility router. Package-local instructions are
the source of truth for concrete Lean work; shared scripts and references live
under `skills/lean-runtime/`.

## Validation

Use package-local validation when changing Lean logic. The formalization package
provides the helper:

```bash
python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

At minimum, run the local skill validator on each changed standard skill
package and check README links.

## Security and Scope

Do not commit Lean build artifacts, downloaded Numina runtime state, API keys,
`.env` files, machine-specific paths, or private theorem notes. Do not present
proofs as accepted without local Lean/Lake validation or an explicit approved
review gate.
