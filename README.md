<div align="center">

# AI4Math · Lean Agents

Coding-agent-first workflows for Lean 4 setup, formalization, proof repair,
and local Lean/mathlib validation.

[中文说明](README.zh-CN.md) · [Contributors](CONTRIBUTORS.md) · [Skill packages](#skill-packages) · [Installation](#installation) · [Quick start](#quick-start) · [References](#related-work-and-public-references) · [Security model](#security-and-scope)

![version](https://img.shields.io/badge/version-0.1.0-blue)
![skills](https://img.shields.io/badge/skills-2-2ea44f)
![license](https://img.shields.io/badge/license-MIT-green)

</div>

## What This Repository Is

This repository is the AI4Math home for Lean agent skills. It gives coding
agents a structured way to inspect Lean projects, set up reusable Lean/mathlib
workspaces, formalize theorem statements, repair proofs, complete `sorry`s, and
validate patches locally.

Use this page as the public map. For real work, open the package that matches
the task and follow its package-local instructions. `skills/lean-runtime/` is a
shared support layer for scripts, schemas, prompts, tests, and references; users
do not invoke it as a standalone Skill.

Backend integration is adapter-first. Built-in recommended adapter: official Numina Lean Agent runtime. Numina and Archon are recommended adapter candidates, not defaults or hard requirements. Other Lean-specialist backends may be connected by the coding agent through the backend adapter checklist; do not call any backend until deployment, readiness checks, invocation, validation, and failure triage are documented.

## Skill Packages

| Package | Use it for | Start here |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | Install or verify Lean 4, `elan`, `lake`, and reusable mathlib workspace readiness before proof work. | [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | Formalize theorem statements, repair Lean proofs, complete `sorry`s, review Lean patches, and coordinate optional backend adapters. | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

## Installation

The recommended path is AI-assisted installation: ask your coding agent to
clone or update this repository, read the Skill instructions, install the two
public entrypoints, keep the runtime support directory next to them, and verify
discovery.

```text
Please install these AI4Math Lean Skills for me.

Repository: https://github.com/VeryMath/AI4Math-Lean-Agents.git
Branch: main
Skill paths:
- skills/lean-setup
- skills/lean-formalization

Steps:
1. Clone or update the repository locally.
2. Read README.md, AGENTS.md, SKILL.md, and each target Skill entrypoint.
3. Keep the sibling skills/lean-runtime support directory in place.
4. If this environment supports local Skill discovery, link each directory that contains SKILL.md into the local skills directory.
5. Verify that $lean-setup and $lean-formalization are discoverable.
6. Tell me the installed paths, whether a restart is needed, and give me one test prompt.
```

Manual fallback for Codex-style local discovery:

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
mkdir -p ~/.codex/skills
ln -s "$PWD/skills/lean-setup" ~/.codex/skills/lean-setup
ln -s "$PWD/skills/lean-formalization" ~/.codex/skills/lean-formalization
```

If your agent uses a different local Skill directory, replace
`~/.codex/skills` with that configured path.

## Quick Start

Clone the repository and choose a package:

```bash
git clone https://github.com/VeryMath/AI4Math-Lean-Agents.git
cd AI4Math-Lean-Agents
```

For Lean environment setup, start with:

```text
skills/lean-setup/SKILL.md
```

For formalization, proof repair, or `sorry` completion, start with:

```text
skills/lean-formalization/SKILL.md
```

For a complete interaction example, see:

```text
examples/lean-setup-add-zero.md
```

## Repository Layout

```text
AI4Math-Lean-Agents/
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── AGENTS.md
├── examples/
└── skills/
    ├── lean-setup/
    ├── lean-formalization/
    └── lean-runtime/
```

Keep user-facing workflow instructions in `lean-setup` and
`lean-formalization`. Keep reusable scripts, tests, schemas, prompts, and
backend-adapter references in `lean-runtime`.

## Validation

Default local validation:

Run the delivery validator from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

For a full local Lean workspace check, include environment and workspace build
requirements:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

Optional adapter setup, only after the user asks for Numina or another backend
adapter and approves the setup plan:

```bash
python3 skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
```

## Security and Scope

Do not commit API keys, `.env` files, local runtime state, downloaded Lean
artifacts, generated caches, or machine-specific Numina paths. The default Lean
workflow is local and coding-agent-first; optional Numina, Archon, Lean LSP/MCP,
or other backend adapters require explicit user approval before setup or calls.

Final Lean patches should be validated locally when possible and must not
introduce `sorry`, `admit`, newly introduced `axiom`, or silent theorem
statement drift.

## Related Work and Public References

This project is informed by public Lean ecosystem projects while keeping its
own local validation boundary:

- [Lean](https://lean-lang.org/) and [Lean 4](https://github.com/leanprover/lean4)
- [mathlib4](https://github.com/leanprover-community/mathlib4)
- [Numina Lean Agent](https://github.com/project-numina/numina-lean-agent)
- [Numina Putnam 2025](https://github.com/project-numina/Numina-Putnam2025)
- [Archon](https://github.com/frenzymath/Archon)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo) and [ReProver](https://github.com/lean-dojo/ReProver)
- [LeanCopilot](https://github.com/lean-dojo/LeanCopilot)
- [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp)
- [COPRA](https://github.com/trishullab/copra)

These references are cited for related-work context around setup, proof-state
loops, retrieval, validation, and failure handoff. Unless explicitly stated,
this repository does not vendor, reproduce, replace, or claim compatibility
with the original systems.
