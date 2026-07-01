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

`lean-formalization` distills public Lean-specialist agent patterns from
systems such as Numina, LeanDojo/ReProver, LeanCopilot, COPRA-style proof
search, Lean LSP/MCP integrations, and small iterative proof agents. The default
coding-agent path remains local-first: project gating, statement normalization,
local context packs, retrieve-before-inventing, bounded proof attempts,
failed-route memory, Lean/Lake validation, and minimal failure handoff. See
`skills/lean-runtime/references/lean_agent_capability_map.md` for the capability
map.

Backend integration is adapter-first. Built-in recommended adapter: official Numina Lean Agent runtime. Numina and Archon are recommended adapter candidates, not defaults or hard requirements. Lean LSP/MCP is documented as an optional adapter recipe for goal-state tooling and MCP-backed theorem search. Other Lean-specialist backends may be connected by the coding agent through the backend adapter checklist; do not call any backend until deployment, readiness checks, invocation, validation, and failure triage are documented.

## When To Use These Skills

Use these skills when you have:

- a need to create or verify a Lean/mathlib workspace before proof work;
- a Lean project or Lean file that needs inspection;
- a theorem statement to transcribe or formalize;
- a proof with `sorry`, `admit`, errors, or statement drift risk;
- a need for an optional Lean-specialist backend mediated by a coding-agent
  adapter contract.

The agent should produce Lean patches, validation summaries, blocked-goal
explanations, minimized failures, and optional backend setup evidence when an
approved adapter path is requested.

## Skill Packages

| Package | Use it for | Start here |
| --- | --- | --- |
| [`lean-setup`](skills/lean-setup/) | Install or verify Lean 4, `elan`, `lake`, and reusable mathlib workspace readiness before proof work. | [`README`](skills/lean-setup/README.md) · [`SKILL`](skills/lean-setup/SKILL.md) |
| [`lean-formalization`](skills/lean-formalization/) | Formalize theorem statements, repair Lean proofs, complete `sorry`, review patches, and optionally coordinate approved backend adapters. | [`README`](skills/lean-formalization/README.md) · [`SKILL`](skills/lean-formalization/SKILL.md) |

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

Optional IDE frontend setup:

```text
After the local Lean/Lake setup and smoke test pass, guide me through the
VS Code frontend setup for Lean.

Please tell me:
- how to install or verify the official Lean 4 VS Code extension;
- which OS-specific setup notes apply to me on macOS, Windows, or Linux;
- which Lake project or shared workspace directory I should open;
- which `.lean` file I should open first;
- how to confirm the Lean InfoView is connected to the same toolchain that
  passed the command-line smoke test.
```

The coding-agent path validates Lean through `lake env lean`, `lake build`, or
the bundled smoke test. [VS Code](https://code.visualstudio.com/) and the
[official Lean 4 extension](https://marketplace.visualstudio.com/items?itemName=leanprover.lean4)
are the recommended human frontend for editing, goals, diagnostics, hovers, and
InfoView on macOS, Windows, and Linux, but they are not a replacement for local
Lean/Lake validation. The [official Lean installer](https://lean-lang.org/install/)
recommends VS Code plus the Lean 4 extension for the rich development
environment, and the extension setup guide provides platform-specific guidance;
the same `elan`/`lake` toolchain should be used by both the IDE and
command-line checks.

These are not the same thing:

- VS Code and Lean InfoView are the human frontend for reading goals and
  diagnostics.
- Lean LSP/MCP is an optional agent tool server and is configured only when the
  user asks for MCP-backed goal/search tooling.
- Numina is an optional backend adapter recipe and is not part of default Lean
  setup, IDE setup, or local validation.

Complete interaction example:

- [From installing Lean skills to verifying a first theorem](examples/lean-setup-add-zero.md): shows how a coding agent installs `lean-setup` / `lean-formalization`, creates or reuses the shared Lean workspace, and verifies a minimal `Nat` theorem.

## Supported Scope

- Lean project/workspace inspection.
- Reusable shared `~/.ai4math/lean-workspace` setup for standalone Lean files, using the AI4Math managed baseline `leanprover/lean4:v4.28.0` unless explicitly overridden.
- Optional macOS/Windows/Linux VS Code / Lean 4 extension frontend guidance after local Lean/Lake readiness is confirmed.
- Theorem formalization, proof repair, proof completion, and `sorry` completion.
- Patch review for `sorry`, `admit`, newly introduced `axiom`, and theorem statement drift.
- Minimal failing Lean fragment extraction when a proof is blocked.
- Distilled Lean-agent patterns: theorem-state loops, premise retrieval, bounded proof search, failed-route memory, validation oracles, and minimal handoff.
- Optional Lean-specialist backend adapter flow, with a built-in recommended recipe for official `project-numina/numina-lean-agent` deployment/calls mediated by the coding agent.
- Optional Lean LSP/MCP adapter recipe for goal state, diagnostics, hover/declaration lookup, local search, MCP theorem search, and multi-attempt screening when explicitly requested.

Numina is optional and provided as a recommended built-in adapter recipe. Lean
LSP/MCP is optional and documented in
`skills/lean-runtime/references/lean_lsp_mcp_adapter.md`. Archon and other
Lean-specialist systems can be connected by the coding agent through
`skills/lean-runtime/references/backend_adapter_checklist.md`; they are not
default dependencies. The public CLI does not expose a parallel `numina-*`
workflow; `doctor` reports readiness and
`configure --setup-numina --project-name <name>` performs the reviewed local
setup under `~/.ai4math/numina-runtime/` by default.

Do not call any backend until deployment, readiness checks, invocation,
validation, and failure triage are documented.

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

## Helper Commands

Run commands from the repository root.

Default local validation:

```bash
python skills/lean-runtime/scripts/ai4m_lean.py env --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/lean-runtime/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

Optional adapter setup, only after the user asks for Numina or another backend
adapter and approves the setup plan:

```bash
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
```

The helper CLI is not the proof engine. The coding agent remains responsible
for reading Lean errors, editing proofs, choosing proof strategy, and matching
the user's language.

For the distilled capability contract, read
`skills/lean-runtime/references/lean_agent_capability_map.md`. For the built-in
recommended Numina adapter path, read
`skills/lean-runtime/references/numina_runtime.md`. For Lean LSP/MCP, read
`skills/lean-runtime/references/lean_lsp_mcp_adapter.md`. For any other backend,
read `skills/lean-runtime/references/backend_adapter_checklist.md` first. Setup
and runner calls may clone repositories, install tools, or use external
model/API credentials, so they should be explained before execution.

## Validation

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --run-tests
```

For a full local Lean workspace check:

```bash
PYTHONDONTWRITEBYTECODE=1 python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

## Related Work and Public References

This project is informed by the following public Lean ecosystem projects and
Lean-agent systems, while maintaining its own coding-agent-first workflow and
local validation boundary:

- [Lean](https://lean-lang.org/) and [Lean 4](https://github.com/leanprover/lean4)
- [mathlib4](https://github.com/leanprover-community/mathlib4)
- [Numina Lean Agent](https://github.com/project-numina/numina-lean-agent)
- [Numina Putnam 2025](https://github.com/project-numina/Numina-Putnam2025)
- [LeanDojo](https://github.com/lean-dojo/LeanDojo) and [ReProver](https://github.com/lean-dojo/ReProver)
- [LeanCopilot](https://github.com/lean-dojo/LeanCopilot)
- [lean-lsp-mcp](https://github.com/project-numina/lean-lsp-mcp)
- [COPRA](https://github.com/trishullab/copra)

These references are cited for related-work context and design provenance around
setup, proof-state loops, retrieval, validation, and failure handoff. The default
skill distills selected mechanisms into a coding-agent workflow; unless
explicitly stated, this repository does not vendor, reproduce, replace, or claim
compatibility with the original systems.

## Security and Scope

Do not commit Lean build artifacts, downloaded Numina runtime state, API keys,
`.env` files, machine-specific paths, or private theorem notes. Do not present
proofs as accepted without local Lean/Lake validation or an explicit approved
review gate.
