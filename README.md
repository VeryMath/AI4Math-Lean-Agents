# AI4Math Lean Skills

Chinese guide: [README.zh-CN.md](README.zh-CN.md)

This repository provides two AI4Math Lean skills:

- `lean-setup`: a setup-only entrypoint for Lean 4, `elan`, `lake`, and reusable mathlib workspace readiness.
- `lean-formalization`: a coding-agent-first skill package for Lean 4 formalization, proof repair, and validation.

Both public skills share the bundled `skills/lean-runtime/` support layer for helper scripts, references, prompts, schemas, examples, and tests. Users invoke only the two public skills; installers should keep `lean-runtime` next to them.

`lean-formalization` is informed by publicly available Lean-specialist agent patterns from systems such as Numina, LeanDojo/ReProver, LeanCopilot, COPRA-style proof search, Lean LSP/MCP integrations, and small iterative proof agents. These are workflow patterns and related work references, not claims that every backend is implemented.

Backend integration is adapter-first. Built-in recommended adapter: official Numina Lean Agent runtime. Numina and Archon are recommended adapter candidates, not defaults or hard requirements. Other Lean-specialist backends may be connected by the coding agent through the backend adapter checklist; do not call any backend until deployment, readiness checks, invocation, validation, and failure triage are documented.

## When To Use These Skills

Use these skills when you have:

- a need to create or verify a Lean/mathlib workspace before proof work (`lean-setup`);
- a Lean project or Lean file that needs inspection;
- a theorem statement to transcribe or formalize;
- a proof with `sorry`, `admit`, errors, or statement drift risk;
- a need for an optional Lean-specialist backend mediated by the coding agent through an adapter contract.

## What They Produce

The agent should produce Lean patches, validation summaries, blocked-goal explanations, minimized failures, and optional backend setup evidence when an approved adapter path is requested.

## Installation

Copy this to your coding agent:

```text
Please install the `lean-setup` and `lean-formalization` skills from https://github.com/VeryMath/AI4Math-Lean-Agents.git. Read `.agent.md`, install the declared Skill entrypoints together with their sibling `lean-runtime` support directory, verify that `$lean-setup` and `$lean-formalization` are discoverable, and tell me whether I need to restart the agent.
```

If you already have this skill repository locally, replace the repository URL
with the local folder path. The coding agent should handle cloning, linking,
configuration, reload/restart checks, and verification.

## Quick Start

Environment-only setup:

```text
Use this repository's Lean setup workflow.

Read:
- AGENTS.md
- skills/lean-setup/SKILL.md

Goal:
Create or verify a reusable Lean 4/mathlib workspace.
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

Formalization or proof work:

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

Complete interaction example:

- [From installing Lean skills to verifying a first theorem](examples/lean-setup-add-zero.md): shows how a coding agent installs `lean-setup` / `lean-formalization`, creates or reuses the shared Lean workspace, and verifies a minimal `Nat` theorem.

## What They Support

- Lean project/workspace inspection.
- Reusable shared `~/.ai4math/lean-workspace` setup for standalone Lean files, using the AI4Math managed baseline `leanprover/lean4:v4.28.0` unless explicitly overridden.
- Optional macOS/Windows/Linux VS Code / Lean 4 extension frontend guidance after local Lean/Lake readiness is confirmed.
- Theorem formalization, proof repair, proof completion, and `sorry` completion.
- Patch review for `sorry`, `admit`, newly introduced `axiom`, and theorem statement drift.
- Minimal failing Lean fragment extraction when a proof is blocked.
- Related-work-informed Lean-specialist patterns: theorem-state loops, premise retrieval, bounded proof search, failure memory, validation oracles, and minimal handoff.
- Optional Lean-specialist backend adapter flow, with a built-in recommended recipe for official `project-numina/numina-lean-agent` deployment/calls mediated by the coding agent.

Numina is optional and provided as a recommended built-in adapter recipe. Archon and other Lean-specialist systems can be connected by the coding agent through `skills/lean-runtime/references/backend_adapter_checklist.md`; they are not default dependencies. The public CLI does not expose a parallel `numina-*` workflow; `doctor` reports readiness and `configure --setup-numina --project-name <name>` performs the reviewed local setup under `~/.ai4math/numina-runtime/` by default.

Do not call any backend until deployment, readiness checks, invocation, validation, and failure triage are documented.

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
    ├── lean-setup/          # setup-only entrypoint
    ├── lean-formalization/  # proof/formalization entrypoint
    └── lean-runtime/        # shared support layer, not a user-invoked skill
```

## How To Interact

Use a checkpoint loop:

```text
Lean task -> project inspection -> plan -> approve / revise / reject / skip
          -> approved edit or validation -> evidence summary -> next checkpoint
```

Use `approve` to run a proposed step, `revise` to update the plan, `reject` to
stop the path, and `skip` to move past a phase. The agent should ask before
theorem statement changes, optional backend setup, source edits, or final proof
claims.

## Helper Commands

Run commands from the repository root:

```bash
python skills/lean-runtime/scripts/ai4m_lean.py env --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py doctor --cwd .
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --create-workspace
python skills/lean-runtime/scripts/ai4m_lean.py configure --cwd . --setup-numina --project-name myproofs --dry-run
python skills/lean-runtime/scripts/ai4m_lean.py check --cwd . --skip-build
python skills/lean-runtime/scripts/ai4m_lean.py verify-delivery --cwd . --require-environment --include-workspace-build --run-tests
```

The helper CLI is not the proof engine. The coding agent remains responsible for reading Lean errors, editing proofs, choosing proof strategy, and matching the user's language.

For the built-in recommended Numina adapter path, read `skills/lean-runtime/references/numina_runtime.md`. For any other backend, read `skills/lean-runtime/references/backend_adapter_checklist.md` first. Setup and runner calls may clone repositories, install tools, or use external model/API credentials, so they should be explained before execution.

## Validate

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
setup, proof-state loops, retrieval, validation, and failure handoff. Unless
explicitly stated, this repository does not vendor, reproduce, replace, or claim
compatibility with the original systems.
